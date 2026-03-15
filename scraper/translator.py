MAKERS: dict[str, str] = {
    "トヨタ": "Toyota",
    "ホンダ": "Honda",
    "日産": "Nissan",
    "マツダ": "Mazda",
    "スバル": "Subaru",
    "三菱": "Mitsubishi",
    "スズキ": "Suzuki",
    "ダイハツ": "Daihatsu",
    "レクサス": "Lexus",
    "いすゞ": "Isuzu",
    "日野": "Hino",
    "ニッサン": "Nissan",
    "BMW": "BMW",
    "メルセデス・ベンツ": "Mercedes-Benz",
    "ベンツ": "Mercedes-Benz",
    "アウディ": "Audi",
    "フォルクスワーゲン": "Volkswagen",
    "ポルシェ": "Porsche",
    "フォード": "Ford",
    "シボレー": "Chevrolet",
    "ジープ": "Jeep",
    "ランドローバー": "Land Rover",
    "ボルボ": "Volvo",
    "プジョー": "Peugeot",
    "ルノー": "Renault",
    "フィアット": "Fiat",
    "アルファロメオ": "Alfa Romeo",
    "フェラーリ": "Ferrari",
    "ランボルギーニ": "Lamborghini",
    "マセラティ": "Maserati",
    "アストンマーティン": "Aston Martin",
    "ベントレー": "Bentley",
    "ロールスロイス": "Rolls-Royce",
    "キア": "Kia",
    "ヒュンダイ": "Hyundai",
    "テスラ": "Tesla",
}

FUEL_TYPES: dict[str, str] = {
    "ガソリン": "Gasoline",
    "ハイブリッド": "Hybrid",
    "プラグインハイブリッド": "Plug-in Hybrid",
    "電気": "Electric",
    "ディーゼル": "Diesel",
    "天然ガス": "CNG",
    "LPG": "LPG",
    "その他": "Other",
    "ガソリン+電気": "Hybrid",
    "マイルドハイブリッド": "Mild Hybrid",
}

TRANSMISSIONS: dict[str, str] = {
    "AT": "Automatic",
    "MT": "Manual",
    "CVT": "CVT",
    "DCT": "DCT",
    "セミAT": "Semi-Auto",
    "オートマ": "Automatic",
    "マニュアル": "Manual",
}

BODY_TYPES: dict[str, str] = {
    "セダン": "Sedan",
    "SUV": "SUV",
    "ミニバン": "Minivan",
    "バン": "Van",
    "ワゴン": "Wagon",
    "ステーションワゴン": "Station Wagon",
    "クーペ": "Coupe",
    "ハッチバック": "Hatchback",
    "軽自動車": "Kei Car",
    "軽": "Kei Car",
    "オープン": "Convertible",
    "コンバーチブル": "Convertible",
    "カブリオレ": "Cabriolet",
    "クロスカントリー": "Crossover",
    "ピックアップ": "Pickup",
    "トラック": "Truck",
    "バス": "Bus",
    "その他": "Other",
    "軽トラック": "Kei Truck",
    "軽バン": "Kei Van",
    "コンパクト": "Compact",
    "スポーツ": "Sports",
}

COLORS: dict[str, str] = {
    "ホワイト": "White",
    "ブラック": "Black",
    "シルバー": "Silver",
    "グレー": "Gray",
    "レッド": "Red",
    "ブルー": "Blue",
    "グリーン": "Green",
    "ブラウン": "Brown",
    "ゴールド": "Gold",
    "パール": "Pearl White",
    "ホワイトパール": "Pearl White",
    "プラチナホワイトパール": "Platinum White Pearl",
    "ベージュ": "Beige",
    "イエロー": "Yellow",
    "オレンジ": "Orange",
    "パープル": "Purple",
    "ピンク": "Pink",
    "その他": "Other",
    "ツートーン": "Two-tone",
    "ブルーイッシュブラック": "Bluish Black",
    "スーパーホワイト": "Super White",
}

DRIVE_TYPES: dict[str, str] = {
    "4WD": "4WD",
    "2WD": "2WD",
    "AWD": "AWD",
    "FF": "Front-Wheel Drive",
    "FR": "Rear-Wheel Drive",
    "MR": "Mid-Rear Drive",
    "フルタイム4WD": "Full-time 4WD",
    "パートタイム4WD": "Part-time 4WD",
}

MODEL_PATTERNS: dict[str, tuple[str, str]] = {
 
    "eKワゴン": ("Mitsubishi", "eK Wagon"),
    "eKスペース": ("Mitsubishi", "eK Space"),
    "eKクロス": ("Mitsubishi", "eK Cross"),
    "ムーヴ": ("Daihatsu", "Move"),
    "ムーブ": ("Daihatsu", "Move"),
    "タント": ("Daihatsu", "Tanto"),
    "フレアワゴン": ("Mazda", "Flair Wagon"),
    "フレア": ("Mazda", "Flair"),
    "スペーシア": ("Suzuki", "Spacia"),
    "スペーシアカスタム": ("Suzuki", "Spacia Custom"),
    "N-VAN": ("Honda", "N-VAN"),
    "N-BOX": ("Honda", "N-BOX"),
    "N-ONE": ("Honda", "N-ONE"),
    "N-WGN": ("Honda", "N-WGN"),
    "ハスラー": ("Suzuki", "Hustler"),
    "アルト": ("Suzuki", "Alto"),
    "ワゴンR": ("Suzuki", "Wagon R"),
    "ワゴンアール": ("Suzuki", "Wagon R"),
    "ジムニー": ("Suzuki", "Jimny"),
    "エブリイ": ("Suzuki", "Every"),
    "キャリイ": ("Suzuki", "Carry"),
    "キャリー": ("Suzuki", "Carry"),
    "ステラ": ("Subaru", "Stella"),
    "プレオ": ("Subaru", "Pleo"),
    "シフォン": ("Subaru", "Chiffon"),
    "デイズ": ("Nissan", "Days"),
    "ルークス": ("Nissan", "Roox"),
    "モコ": ("Nissan", "Moco"),
    "オッティ": ("Nissan", "Otti"),
    "アトレー": ("Daihatsu", "Atrai"),
    "ハイゼット": ("Daihatsu", "Hijet"),
    "ピクシス": ("Toyota", "Pixis"),
    "パッソ": ("Toyota", "Passo"),
    "ブーン": ("Toyota", "Boon"),
    "シエンタ": ("Toyota", "Sienta"),
    "ラクティス": ("Toyota", "Ractis"),
    "ヴィッツ": ("Toyota", "Vitz"),
    "ヤリス": ("Toyota", "Yaris"),
    "アクア": ("Toyota", "Aqua"),
    "プリウス": ("Toyota", "Prius"),
    "フィット": ("Honda", "Fit"),
    "フリード": ("Honda", "Freed"),
    "ステップワゴン": ("Honda", "Step Wagon"),
    "オデッセイ": ("Honda", "Odyssey"),
    "N-BOXカスタム": ("Honda", "N-BOX Custom"),
    "N-VANスタイル": ("Honda", "N-VAN Style"),
}


def translate_maker(value: str) -> str:
    for jp_model, (maker_en, model_en) in MODEL_PATTERNS.items():
        if jp_model in value:
            return maker_en
    

    for jp, en in MAKERS.items():
        if jp in value:
            return en
    return value.strip()


def translate_fuel(value: str) -> str:
    for jp, en in FUEL_TYPES.items():
        if jp in value:
            return en
    return value.strip()


def translate_transmission(value: str) -> str:
    for jp, en in TRANSMISSIONS.items():
        if jp in value:
            return en
    return value.strip()


def translate_body_type(value: str) -> str:
    for jp, en in BODY_TYPES.items():
        if jp in value:
            return en
    return value.strip()


def translate_color(value: str) -> str:
    for jp, en in COLORS.items():
        if jp in value:
            return en
    return value.strip()


def translate_drive(value: str) -> str:
    for jp, en in DRIVE_TYPES.items():
        if jp in value:
            return en
    return value.strip()


def normalize_year(value: str) -> int | None:
    import re
    m = re.search(r"(\d{4})", value)
    return int(m.group(1)) if m else None


def normalize_mileage(value: str) -> int | None:
    import re
    value = value.replace(",", "").replace(" ", "").replace("　", "")
    m = re.search(r"([\d.]+)万", value)
    if m:
        return int(float(m.group(1)) * 10000)
    m = re.search(r"(\d+)km", value, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def normalize_price(value: str) -> int | None:
    import re
    value = value.replace(",", "").replace(" ", "").replace("　", "")
    m = re.search(r"([\d.]+)万", value)
    if m:
        return int(float(m.group(1)) * 10000)
    m = re.search(r"(\d+)円", value)
    if m:
        return int(m.group(1))
    return None


def normalize_displacement(value: str) -> int | None:
    import re
    m = re.search(r"(\d+)cc", value, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"([\d.]+)[lL]", value)
    if m:
        return int(float(m.group(1)) * 1000)
    return None