"""
Faza 3 seed content: xizmat tavsiflari, shifokor bio/sertifikat, before/after va galereya.
seed_demo.py buni import qiladi. Kalitlar — uz sarlavha/ism (seed_demo dagi bilan bir xil).
Barcha matn uch tilda, lorem YOʻQ.
"""

# ── Xizmat to'liq tavsiflari (Service.body) — uz title bo'yicha ──
SERVICE_BODIES = {
    "Implantatsiya": {
        "uz": "Tish implantatsiyasi — yoʻqolgan tishni tabiiy koʻrinishda tiklaydigan eng ishonchli usul. Titan implant jagʻ suyagiga oʻrnatiladi va u yerda mustahkam poydevor boʻlib xizmat qiladi.\n\nBiz Straumann va Osstem tizimlaridan foydalanamiz. 3D KLKT diagnostikasi bilan aniq rejalashtirish oʻtkazamiz — bu jarrohlikni xavfsiz va ogʻriqsiz qiladi.\n\nImplant oʻrnatilgach, ustiga tabiiy tishdan farq qilmaydigan sirkoniy yoki metall-keramika toj qoʻyiladi.",
        "ru": "Имплантация зубов — самый надёжный способ восстановить утраченный зуб с естественным видом. Титановый имплант устанавливается в челюстную кость и служит прочной опорой.\n\nМы работаем с системами Straumann и Osstem. Точное планирование по 3D КЛКТ делает операцию безопасной и безболезненной.\n\nПосле приживления импланта устанавливается коронка из циркония или металлокерамики, неотличимая от натурального зуба.",
        "en": "Dental implants are the most reliable way to restore a missing tooth with a natural look. A titanium implant is placed in the jawbone and serves as a firm foundation.\n\nWe use Straumann and Osstem systems. Precise 3D CBCT planning makes the procedure safe and painless.\n\nOnce the implant integrates, a zirconia or metal-ceramic crown — indistinguishable from a natural tooth — is fitted on top.",
    },
    "Estetik plombalash": {
        "uz": "Estetik plombalash tishning shakli va rangini tabiiy holatiga qaytaradi. Zamonaviy kompozit materiallar tish emaliga toʻliq mos rang tanlash imkonini beradi.\n\nProtsedura bir tashrifda bajariladi va ogʻriqsiz oʻtadi. Natija koʻp yillar davomida saqlanadi.",
        "ru": "Эстетическая реставрация возвращает зубу естественную форму и цвет. Современные композитные материалы позволяют точно подобрать оттенок под эмаль.\n\nПроцедура выполняется за один визит и проходит безболезненно. Результат сохраняется долгие годы.",
        "en": "Aesthetic fillings restore a tooth's natural shape and colour. Modern composite materials let us match the shade to your enamel precisely.\n\nThe procedure is done in a single visit and is painless. The result lasts for years.",
    },
    "Professional gigiyena": {
        "uz": "Professional ogʻiz boʻshligʻi gigiyenasi tish kariesi va milk kasalliklarining eng samarali profilaktikasi. Ultratovushli tozalash va Air Flow yordamida tish toshi hamda karash olib tashlanadi.\n\nHar 6 oyda bir marta oʻtkazish tavsiya etiladi. Protsedura tishlarni bir necha ton yorugʻroq qiladi.",
        "ru": "Профессиональная гигиена — самая эффективная профилактика кариеса и болезней дёсен. Ультразвуковая чистка и Air Flow удаляют зубной камень и налёт.\n\nРекомендуется раз в 6 месяцев. Процедура делает зубы на несколько тонов светлее.",
        "en": "Professional hygiene is the most effective prevention of cavities and gum disease. Ultrasonic cleaning and Air Flow remove tartar and plaque.\n\nRecommended every 6 months. The procedure leaves teeth several shades brighter.",
    },
    "Breketlar": {
        "uz": "Breket tizimlari tishlarning notoʻgʻri joylashuvini va prikusni tuzatadi. Biz metall, keramik va sapfirli breketlarni taklif qilamiz.\n\nDavolash muddati holatga qarab 12–24 oy. Har oyda nazorat koʻrigi oʻtkaziladi.",
        "ru": "Брекет-системы исправляют неправильное положение зубов и прикус. Мы предлагаем металлические, керамические и сапфировые брекеты.\n\nСрок лечения — 12–24 месяца в зависимости от случая. Ежемесячно проводится контрольный осмотр.",
        "en": "Braces correct misaligned teeth and bite. We offer metal, ceramic, and sapphire brackets.\n\nTreatment takes 12–24 months depending on the case, with a monthly check-up.",
    },
    "Ildiz kanali davolash": {
        "uz": "Ildiz kanalini davolash (endodontiya) tish pulpasi yalligʻlanganda tishni saqlab qolish imkonini beradi. Biz mikroskop ostida ishlaymiz — bu kanallarni aniq tozalash va toʻldirish kafolatini beradi.\n\nZamonaviy anesteziya protsedurani toʻliq ogʻriqsiz qiladi.",
        "ru": "Лечение корневых каналов (эндодонтия) позволяет сохранить зуб при воспалении пульпы. Мы работаем под микроскопом — это гарантирует точную очистку и пломбировку каналов.\n\nСовременная анестезия делает процедуру полностью безболезненной.",
        "en": "Root canal treatment (endodontics) saves a tooth when the pulp is inflamed. We work under a microscope, ensuring precise cleaning and filling of the canals.\n\nModern anaesthesia makes the procedure entirely painless.",
    },
    "Aqli tish olib tashlash": {
        "uz": "Aqli tishlarni olib tashlash — koʻpincha ular notoʻgʻri oʻsadi va qoʻshni tishlarga zarar yetkazadi. Jarrohlik 3D diagnostika asosida rejalashtiriladi.\n\nProtsedura zamonaviy anesteziya ostida ogʻriqsiz oʻtadi; keyingi parvarish boʻyicha batafsil koʻrsatma beriladi.",
        "ru": "Удаление зубов мудрости — они часто растут неправильно и повреждают соседние зубы. Операция планируется на основе 3D-диагностики.\n\nПроцедура проходит безболезненно под современной анестезией; даём подробные рекомендации по уходу.",
        "en": "Wisdom teeth often erupt incorrectly and damage neighbouring teeth. Removal is planned using 3D diagnostics.\n\nThe procedure is painless under modern anaesthesia, with detailed aftercare guidance.",
    },
    "Karies davolash": {
        "uz": "Kariesni erta bosqichda davolash tishni butunligicha saqlab qoladi. Zararlangan toʻqima olib tashlanadi va tish estetik kompozit bilan tiklanadi.\n\nOgʻriqsiz, bir tashrifda.",
        "ru": "Лечение кариеса на ранней стадии полностью сохраняет зуб. Поражённая ткань удаляется, зуб восстанавливается эстетичным композитом.\n\nБезболезненно, за один визит.",
        "en": "Treating cavities early keeps the tooth intact. Decayed tissue is removed and the tooth restored with an aesthetic composite.\n\nPainless, in a single visit.",
    },
    "Tishlarni oqartirish": {
        "uz": "Professional tishlarni oqartirish tabassumingizni bir necha ton yorugʻroq qiladi. Biz xavfsiz, emalga zarar bermaydigan zamonaviy tizimlardan foydalanamiz.\n\nNatija bir tashrifdan keyin koʻrinadi va uzoq saqlanadi.",
        "ru": "Профессиональное отбеливание делает улыбку на несколько тонов светлее. Мы используем безопасные современные системы, не повреждающие эмаль.\n\nРезультат виден уже после одного визита и держится долго.",
        "en": "Professional whitening brightens your smile by several shades. We use safe, modern systems that don't harm the enamel.\n\nResults are visible after a single visit and last a long time.",
    },
    "Suyak toʻqimasi tiklash": {
        "uz": "Suyak toʻqimasini tiklash (sinus-lifting va suyak plastikasi) implant oʻrnatish uchun yetarli suyak boʻlmaganda oʻtkaziladi.\n\nZamonaviy osteoplastik materiallar ishonchli va bashоratli natija beradi.",
        "ru": "Костная пластика (синус-лифтинг и наращивание кости) проводится, когда объёма кости недостаточно для установки импланта.\n\nСовременные остеопластические материалы дают надёжный и прогнозируемый результат.",
        "en": "Bone grafting (sinus lift and augmentation) is performed when there isn't enough bone volume for an implant.\n\nModern osteoplastic materials give a reliable, predictable result.",
    },
    "Elayner (shaffof kappa)": {
        "uz": "Elaynerlar — deyarli koʻrinmaydigan shaffof kappalar bilan tishlarni tuzatish usuli. Ular breketga qulay muqobil: yechib olsa boʻladi va noqulaylik tugʻdirmaydi.\n\nHar bir kappa toʻplami tishlarni bosqichma-bosqich toʻgʻri holatga keltiradi.",
        "ru": "Элайнеры — способ выравнивания зубов почти незаметными прозрачными капами. Удобная альтернатива брекетам: снимаются и не доставляют дискомфорта.\n\nКаждый набор кап постепенно перемещает зубы в правильное положение.",
        "en": "Aligners straighten teeth with nearly invisible clear trays. A comfortable alternative to braces: removable and discreet.\n\nEach set of trays gradually moves teeth into the correct position.",
    },
    "Bolalar stomatologiyasi": {
        "uz": "Bolalar stomatologiyasi — bolangiz uchun qulay va qoʻrquvsiz muhit. Bizning shifokorlar bolalar bilan ishlash boʻyicha maxsus tayyorgarlikdan oʻtgan.\n\nSut tishlari davolash, ftorlash va profilaktika — hammasi yumshoq yondashuv bilan.",
        "ru": "Детская стоматология — комфортная и спокойная атмосфера для вашего ребёнка. Наши врачи прошли специальную подготовку по работе с детьми.\n\nЛечение молочных зубов, фторирование и профилактика — всё с мягким подходом.",
        "en": "Paediatric dentistry means a comfortable, fear-free environment for your child. Our doctors are specially trained to work with children.\n\nTreating milk teeth, fluoridation, and prevention — all with a gentle approach.",
    },
    "Vinirlar": {
        "uz": "Vinirlar — tishning old yuzasiga oʻrnatiladigan nozik keramik plastinkalar. Ular tabassumni ideal shaklga keltiradi: rang, shakl va oraliqlarni bir vaqtda tuzatadi.\n\nMinimal tayyorlash bilan — tabiiy va uzoq muddatli natija.",
        "ru": "Виниры — тонкие керамические пластинки на переднюю поверхность зуба. Они придают улыбке идеальный вид: цвет, форму и промежутки исправляют одновременно.\n\nМинимальная обработка — естественный и долговечный результат.",
        "en": "Veneers are thin ceramic shells bonded to the front of the tooth. They give the smile an ideal look — correcting colour, shape, and gaps at once.\n\nMinimal preparation for a natural, long-lasting result.",
    },
    "Protezlash": {
        "uz": "Protezlash yoʻqolgan tishlarni tiklaydi va chaynash funksiyasini qaytaradi. Biz sirkoniy va metall-keramika toj hamda koʻpriklarini taklif qilamiz.\n\nHar bir protez individual ravishda, tabiiy tishlaringizga mos qilib tayyorlanadi.",
        "ru": "Протезирование восстанавливает утраченные зубы и возвращает жевательную функцию. Мы предлагаем коронки и мосты из циркония и металлокерамики.\n\nКаждый протез изготавливается индивидуально, под ваши natural зубы.",
        "en": "Prosthetics restore missing teeth and bring back chewing function. We offer zirconia and metal-ceramic crowns and bridges.\n\nEach prosthesis is made individually to match your natural teeth.",
    },
    "Milk kasalliklari davolash": {
        "uz": "Milk kasalliklarini (gingivit va parodontit) davolash tishlarni yoʻqotishdan saqlaydi. Biz milk holatini kompleks tekshiramiz va yakka davolash rejasini tuzamiz.\n\nErta murojaat — eng yaxshi natija kafolati.",
        "ru": "Лечение болезней дёсен (гингивит и пародонтит) предотвращает потерю зубов. Мы комплексно оцениваем состояние дёсен и составляем индивидуальный план.\n\nРаннее обращение — гарантия лучшего результата.",
        "en": "Treating gum disease (gingivitis and periodontitis) prevents tooth loss. We assess gum health comprehensively and build an individual plan.\n\nEarly attention is the best guarantee of a good outcome.",
    },
}

# ── Shifokor bio (Doctor.bio) — uz ism bo'yicha ──
DOCTOR_BIOS = {
    "Dilshod Raximov": {
        "uz": "Dilshod Raximov — 14 yildan ortiq tajribaga ega implantolog va jarroh-stomatolog. 3000 dan ortiq muvaffaqiyatli implant oʻrnatgan. Murakkab holatlar va suyak plastikasi boʻyicha mutaxassis.",
        "ru": "Дилшод Рахимов — имплантолог и хирург-стоматолог с опытом более 14 лет. Установил более 3000 имплантов. Специалист по сложным случаям и костной пластике.",
        "en": "Dilshod Rakhimov is an implantologist and oral surgeon with over 14 years of experience. He has placed more than 3,000 implants and specialises in complex cases and bone grafting.",
    },
    "Nigora Yusupova": {
        "uz": "Nigora Yusupova — ortodont, breket va elayner tizimlari boʻyicha mutaxassis. Bolalar va kattalarda prikusni tuzatish bilan shugʻullanadi. Damon va Invisalign sertifikatiga ega.",
        "ru": "Нигора Юсупова — ортодонт, специалист по брекет- и элайнер-системам. Занимается исправлением прикуса у детей и взрослых. Сертифицирована по Damon и Invisalign.",
        "en": "Nigora Yusupova is an orthodontist specialising in braces and aligner systems. She corrects bite in children and adults and is Damon and Invisalign certified.",
    },
    "Kamola Ergasheva": {
        "uz": "Kamola Ergasheva — terapevt-stomatolog va endodontist. Mikroskop ostida ildiz kanallarini davolash boʻyicha 11 yillik tajribaga ega. Estetik restavratsiya ustasi.",
        "ru": "Камола Эргашева — терапевт-стоматолог и эндодонтист. 11 лет опыта лечения корневых каналов под микроскопом. Мастер эстетической реставрации.",
        "en": "Kamola Ergasheva is a restorative dentist and endodontist with 11 years of experience in microscope root-canal treatment. A master of aesthetic restoration.",
    },
    "Sardor Toshmatov": {
        "uz": "Sardor Toshmatov — ortoped-stomatolog, protezlash boʻyicha 16 yillik tajriba. Sirkoniy toj, koʻprik va toʻliq protezlar bilan ishlaydi. Chaynash funksiyasini toʻliq tiklashga ixtisoslashgan.",
        "ru": "Сардор Тошматов — ортопед-стоматолог с 16-летним опытом протезирования. Работает с циркониевыми коронками, мостами и полными протезами. Специализируется на полном восстановлении жевательной функции.",
        "en": "Sardor Toshmatov is a prosthodontist with 16 years of experience. He works with zirconia crowns, bridges, and full dentures, specialising in fully restoring chewing function.",
    },
    "Malika Qodirova": {
        "uz": "Malika Qodirova — bolalar stomatologi. Bolalarda qoʻrquvsiz, yumshoq davolashga ixtisoslashgan. 7 yildan beri eng kichik bemorlarning tabassumini asraydi.",
        "ru": "Малика Кадырова — детский стоматолог. Специализируется на мягком лечении детей без страха. Уже 7 лет бережёт улыбки самых маленьких пациентов.",
        "en": "Malika Qodirova is a paediatric dentist specialising in gentle, fear-free treatment for children. For 7 years she has cared for the smiles of the youngest patients.",
    },
}

# ── Shifokor sertifikatlari (Doctor.certificates) ──
DOCTOR_CERTS = {
    "Dilshod Raximov": {"uz": "Straumann Implant Academy · Osstem AIC · GBR suyak plastikasi",
                        "ru": "Straumann Implant Academy · Osstem AIC · костная пластика GBR",
                        "en": "Straumann Implant Academy · Osstem AIC · GBR bone grafting"},
    "Nigora Yusupova": {"uz": "Damon System · Invisalign Provider · Ortodontiya assotsiatsiyasi aʼzosi",
                        "ru": "Damon System · Invisalign Provider · член ассоциации ортодонтов",
                        "en": "Damon System · Invisalign Provider · orthodontic association member"},
    "Kamola Ergasheva": {"uz": "Mikroskopik endodontiya · Estetik restavratsiya (Style Italiano)",
                         "ru": "Микроскопическая эндодонтия · эстетическая реставрация (Style Italiano)",
                         "en": "Microscope endodontics · aesthetic restoration (Style Italiano)"},
    "Sardor Toshmatov": {"uz": "Sirkoniy protezlash · CAD/CAM texnologiyasi",
                         "ru": "Циркониевое протезирование · технология CAD/CAM",
                         "en": "Zirconia prosthetics · CAD/CAM technology"},
    "Malika Qodirova": {"uz": "Bolalar stomatologiyasi · Davolash sedatsiyasi",
                        "ru": "Детская стоматология · лечебная седация",
                        "en": "Paediatric dentistry · treatment sedation"},
}

# ── Shifokor photo_alt (yuz berkitilgan kadrlar — niqobli) ──
DOCTOR_ALTS = {
    "Dilshod Raximov": {"uz": "Dilshod Raximov — implantolog, ish jarayonida", "ru": "Дилшод Рахимов — имплантолог за работой", "en": "Dilshod Rakhimov, implantologist at work"},
    "Nigora Yusupova": {"uz": "Nigora Yusupova — ortodont", "ru": "Нигора Юсупова — ортодонт", "en": "Nigora Yusupova, orthodontist"},
    "Kamola Ergasheva": {"uz": "Kamola Ergasheva — terapevt-stomatolog", "ru": "Камола Эргашева — терапевт-стоматолог", "en": "Kamola Ergasheva, restorative dentist"},
}

# ── Xizmat → cover fayl (faqat vetted rasmlar; qolgani fallback) ──
SERVICE_COVERS = {
    "Ildiz kanali davolash": "services/ildiz-kanali-davolash.jpg",
    "Professional gigiyena": "services/professional-gigiyena.jpg",
    "Suyak toʻqimasi tiklash": "services/suyak-toqimasi-tiklash.jpg",
    "Tishlarni oqartirish": "services/tishlarni-oqartirish.jpg",
    "Vinirlar": "services/vinirlar.jpg",
}
DOCTOR_PHOTOS = {
    "Dilshod Raximov": "doctors/dilshod-raximov.jpg",
    "Nigora Yusupova": "doctors/nigora-yusupova.jpg",
    "Kamola Ergasheva": "doctors/kamola-ergasheva.jpg",
}
# Blog: indeks bo'yicha (BLOG_POSTS tartibi) — mavjud bo'lganlar
BLOG_COVERS = {
    0: "blog/implant-care.jpg",   # implantatsiyadan keyin
    2: "blog/braces-aligners.jpg",  # breket yoki elayner
    3: "blog/toothache.jpg",      # tish ogʻrigʻi
    4: "blog/hygiene.jpg",        # professional gigiyena
}

# ── Before/after case juftliklari ("Demo namunasi" izohi bilan) ──
_DEMO_NOTE = {
    "uz": "Demo namunasi — klinika bu yerga oʻz ishlarini qoʻyadi.",
    "ru": "Демо-пример — клиника разместит здесь свои работы.",
    "en": "Demo sample — the clinic places its own cases here.",
}
CASES = [
    {
        "title": {"uz": "Old tishlar estetikasi", "ru": "Эстетика передних зубов", "en": "Front teeth aesthetics"},
        "service": "Vinirlar", "doctor": "Kamola Ergasheva",
        "before": "cases/case1-before.jpg", "after": "cases/case1-after.jpg",
        "summary": {"uz": "Vinirlar bilan tabassum toʻliq tiklandi.", "ru": "Улыбка полностью восстановлена винирами.", "en": "Smile fully restored with veneers."},
        "duration": {"uz": "2 hafta", "ru": "2 недели", "en": "2 weeks"},
        "featured": True,
    },
    {
        "title": {"uz": "Tishlarni oqartirish natijasi", "ru": "Результат отбеливания", "en": "Whitening result"},
        "service": "Tishlarni oqartirish", "doctor": "Kamola Ergasheva",
        "before": "cases/case3-before.jpg", "after": "cases/case3-after.jpg",
        "summary": {"uz": "Professional oqartirishdan keyin 4 ton yorugʻroq.", "ru": "На 4 тона светлее после профессионального отбеливания.", "en": "Four shades brighter after professional whitening."},
        "duration": {"uz": "1 tashrif", "ru": "1 визит", "en": "1 visit"},
        "featured": True,
    },
    {
        "title": {"uz": "Estetik restavratsiya", "ru": "Эстетическая реставрация", "en": "Aesthetic restoration"},
        "service": "Estetik plombalash", "doctor": "Kamola Ergasheva",
        "before": "cases/case2-before.jpg", "after": "cases/case1-after.jpg",
        "summary": {"uz": "Kompozit restavratsiya bilan tabiiy koʻrinish.", "ru": "Естественный вид с композитной реставрацией.", "en": "A natural look with composite restoration."},
        "duration": {"uz": "1 tashrif", "ru": "1 визит", "en": "1 visit"},
        "featured": False,
    },
]

def demo_note(lang):
    return _DEMO_NOTE[lang]

# ── Galereya (image, category, alt, caption) ──
GALLERY = [
    ("gallery/clinic-1.jpg", "clinic", {"uz": "Zamonaviy operatorxona", "ru": "Современный кабинет", "en": "Modern operatory"}),
    ("gallery/clinic-4.jpg", "clinic", {"uz": "Davolash xonasi", "ru": "Кабинет", "en": "Treatment room"}),
    ("gallery/equipment-3.jpg", "equipment", {"uz": "Steril asboblar", "ru": "Стерильные инструменты", "en": "Sterile instruments"}),
    ("gallery/equipment-4.jpg", "equipment", {"uz": "Mikroskop", "ru": "Микроскоп", "en": "Microscope"}),
    ("gallery/team-2.jpg", "team", {"uz": "Ish jarayonida", "ru": "В процессе работы", "en": "At work"}),
    ("gallery/work-1.jpg", "work", {"uz": "Diagnostika", "ru": "Диагностика", "en": "Diagnostics"}),
    ("gallery/work-2.jpg", "work", {"uz": "Aniq ish", "ru": "Точная работа", "en": "Precise work"}),
]
