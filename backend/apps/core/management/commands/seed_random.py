"""Tasodifiy demo ma'lumot — admin/kalendar TIRIK ko'rinishi uchun ko'p qabul + murojaat.

`seed_demo` dan FARQI: bu ADDITIVE (hech narsani o'chirmaydi) va TASODIFIY. Sotuvda prospekt
admin'ga kirganda band klinika ko'rinsin. Xohlagancha ko'p marta ishga tushirsa bo'ladi.

    python manage.py seed_random --appointments 50 --leads 20
    python manage.py seed_random --seed 42        # takrorlanadigan natija
"""

import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.appointments.models import Appointment, AppointmentStatus
from apps.leads.models import Lead
from apps.services.models import Service
from apps.team.models import Doctor

FIRST_M = [
    "Aziz", "Bekzod", "Jasur", "Oybek", "Sardor", "Akmal", "Doniyor", "Farrux", "Shohruh",
    "Ulugʻbek", "Rustam", "Kamron", "Bobur", "Islom", "Temur", "Dilshod", "Sherzod", "Alisher",
]
FIRST_F = [
    "Aziza", "Nodira", "Dilnoza", "Malika", "Zilola", "Gulnora", "Sevara", "Kamola", "Feruza",
    "Nigora", "Madina", "Shahnoza", "Charos", "Dilfuza", "Muattar", "Laylo", "Ozoda", "Nasiba",
]
LAST = [
    "Karimov", "Rahmonov", "Ismoilov", "Toshpoʻlatov", "Sattorov", "Nazarov", "Yusupov", "Aliyev",
    "Xolmatov", "Ergashev", "Qodirov", "Tursunov", "Mirzayev", "Saidov", "Abdullayev", "Umarov",
]
PHONE_PREFIX = ["90", "91", "93", "94", "95", "97", "98", "99", "88", "33"]
APPT_COMMENTS = [
    "Tishim ogʻriyapti", "Konsultatsiya kerak", "Iltimos, ertalabga yozing", "Bolam uchun",
    "Implantatsiya boʻyicha savol", "Avval shu klinikada boʻlganman", "Estetik plombalash",
    "", "", "", "Gigiyena tozalash",
]
LEAD_MSGS = [
    "Narxlar haqida maʼlumot bering", "Qachon boʻsh vaqtingiz bor?", "Breketlar qancha turadi?",
    "Implant kafolati bormi?", "Bolalar stomatologi bormi?", "Qoʻngʻiroq qilib bering",
    "Aqli tish olib tashlash narxi?", "", "Elayner boʻyicha konsultatsiya",
]
SOURCE_PAGES = ["/uz", "/uz/narxlar", "/uz/xizmatlar/implantatsiya", "/uz/aloqa", "/uz/shifokorlar"]


def _overlaps(intervals, start, end):
    """Shu shifokorda faol qabul vaqti ustma-ust tushmasligi (DB exclusion constraint)."""
    return any(start < e and s < end for s, e in intervals)


class Command(BaseCommand):
    help = "Tasodifiy qabul + murojaat qo'shadi (additive). Admin tirik ko'rinishi uchun."

    def add_arguments(self, parser):
        parser.add_argument("--appointments", type=int, default=50, help="qabullar soni")
        parser.add_argument("--leads", type=int, default=20, help="murojaatlar soni")
        parser.add_argument("--seed", type=int, default=None, help="takrorlanadigan natija uchun")

    def handle(self, *args, **opts):
        if opts["seed"] is not None:
            random.seed(opts["seed"])

        doctors = list(Doctor.objects.all())
        services = list(Service.objects.all())
        if not doctors or not services:
            self.stderr.write("Avval `seed_demo` ishga tushiring — shifokor/xizmat yoʻq.")
            return

        n_appt = self._make_appointments(doctors, services, opts["appointments"])
        n_lead = self._make_leads(opts["leads"])

        self.stdout.write(self.style.SUCCESS(
            f"✓ Tasodifiy demo qoʻshildi: {n_appt} qabul, {n_lead} murojaat.\n"
            f"    Jami qabul: {Appointment.objects.count()} · murojaat: {Lead.objects.count()}"
        ))

    def _rand_name(self):
        pool = random.choice([FIRST_M, FIRST_F])
        return f"{random.choice(pool)} {random.choice(LAST)}"

    def _rand_phone(self):
        return f"+998{random.choice(PHONE_PREFIX)}{random.randint(1000000, 9999999)}"

    def _make_appointments(self, doctors, services, count):
        now = timezone.localtime()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        active_by_doctor: dict[int, list] = {d.id: [] for d in doctors}
        created = 0

        for _ in range(count):
            doctor = random.choice(doctors)
            service = random.choice(services)
            day_off = random.randint(-30, 21)
            hour = random.randint(9, 17)
            minute = random.choice([0, 15, 30, 45])
            starts = midnight + timedelta(days=day_off, hours=hour, minutes=minute)
            ends = starts + timedelta(minutes=service.duration_minutes)

            in_past = starts < now
            if in_past:
                status = random.choices(
                    [AppointmentStatus.COMPLETED, AppointmentStatus.NO_SHOW,
                     AppointmentStatus.CANCELLED_BY_PATIENT, AppointmentStatus.CANCELLED_BY_CLINIC],
                    weights=[70, 12, 12, 6], k=1,
                )[0]
            else:
                status = random.choices(
                    [AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING], weights=[62, 38], k=1
                )[0]

            # Faol (pending/confirmed) qabullar shu shifokorda ustma-ust tushmasin.
            is_active = status in (AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED)
            if is_active and _overlaps(active_by_doctor[doctor.id], starts, ends):
                # bo'sh slot topolmadik — kelajakdagi bandlikni buzmaslik uchun o'tkazamiz
                continue

            try:
                with transaction.atomic():
                    Appointment.objects.create(
                        doctor=doctor,
                        service=service,
                        patient_name=self._rand_name(),
                        phone=self._rand_phone(),
                        comment=random.choice(APPT_COMMENTS),
                        starts_at=starts,
                        ends_at=ends,
                        status=status,
                        source=random.choice([Appointment.Source.WEB, Appointment.Source.PHONE]),
                        locale=random.choice(["uz", "uz", "ru"]),
                        consent_given_at=starts - timedelta(days=1),
                        consent_text_version="v1",
                    )
            except IntegrityError:
                continue  # kod/constraint to'qnashuvi — shu qatorni o'tkazamiz

            if is_active:
                active_by_doctor[doctor.id].append((starts, ends))
            created += 1
        return created

    def _make_leads(self, count):
        kinds = [Lead.Kind.CALLBACK, Lead.Kind.CONTACT, Lead.Kind.PRICE_REQUEST]
        created = 0
        for _ in range(count):
            kind = random.choice(kinds)
            status = random.choices(
                [Lead.Status.NEW, Lead.Status.IN_PROGRESS, Lead.Status.WON, Lead.Status.LOST],
                weights=[55, 25, 12, 8], k=1,
            )[0]
            lead = Lead.objects.create(
                kind=kind,
                name=self._rand_name(),
                phone=self._rand_phone(),
                message=random.choice(LEAD_MSGS) if kind != Lead.Kind.CALLBACK else "",
                status=status,
                locale=random.choice(["uz", "uz", "ru"]),
                source_page=random.choice(SOURCE_PAGES),
                consent_given_at=timezone.now(),
            )
            # created_at ni o'tmishga tarqatamiz (auto_now_add'ni update bilan chetlab).
            past = timezone.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            Lead.objects.filter(pk=lead.pk).update(created_at=past)
            created += 1
        return created
