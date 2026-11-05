# Skill Merger

[![Validate](https://github.com/RizgarOzan/skill-merger/actions/workflows/validate.yml/badge.svg)](https://github.com/RizgarOzan/skill-merger/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[English](README.md) · **Türkçe**

Birkaç ay skill kurunca elinde üç tane Unity UI skill'i, iki commit skill'i, yarı yarıya örtüşen dört tasarım inceleme skill'i birikiyor. Ajan yanlış olanı açıyor, bazen birbiriyle çelişen ikisini birden yüklüyor. Üstüne bütün o açıklamalar her mesajda bağlamda yer kaplıyor.

Skill Merger böyle bir grubu tek bir skill'de birleştirir. Hiçbir şey sessizce kaybolmaz: her kaynaktaki her kural, adım ve script için bir kayıt satırı açılır, o satırda parçanın nereye gittiği ya da neden atıldığı yazar. İki kaynak çelişiyorsa kararı sen verirsin. Eski skiller çöpe değil, arşiv klasörüne gider.

Düz Markdown ve bağımlılığı olmayan tek bir Python script'inden ibaret. Skill okuyabilen her ajanda çalışır: Claude Code, Claude Desktop, Codex, Cursor, OpenCode.

## Kurulum

[skills CLI](https://skills.sh) ile:

```bash
npx skills add RizgarOzan/skill-merger --global
```

Claude Code eklentisi olarak:

```text
/plugin marketplace add RizgarOzan/skill-merger
/plugin install skill-merger@skill-merger
```

Elle kurmak için bu klasörü `~/.claude/skills/skill-merger/` altına ya da ajanının skill klasörüne kopyala.

## Kullanım

Düz cümleyle iste:

```text
Çok fazla UI skill'im var, örtüşenleri birleştir
```

```text
unity-ui, unity-ui-toolkit ve ui-uitk'yi unity-ui adında tek skill yap
```

```text
Hangi skillerim birbiriyle çakışıyor?
```

Ya da doğrudan `/skill-merger` ile çağır (eklenti olarak kurduysan `/skill-merger:skill-merger`).

## Ne yapıyor

| Adım | Ne oluyor | Karar kimde |
|---|---|---|
| 1. Envanter | Bütün skillerini listeler: kendi skillerin, proje skilleri, plugin skilleri | |
| 2. Kümeler | Örtüşen grupları ve her biri için yeni bir ad önerir | **sen** onaylarsın |
| 3. Okuma | Her kaynağın bütün dosyalarını okur, sadece `SKILL.md`'yi değil | |
| 4. Kayıt | Her kaynağı parçalara ayırır, her parçaya bir karar verir | çelişkileri **sen** çözersin |
| 5. Yazma | Ortak kurallar `SKILL.md`'ye, gerisi `references/`'a, scriptler `scripts/`'e | |
| 6. Doğrulama | Denetleyiciyi çalıştırır, kaydı satır satır gezer, eski tetikleyicilerin hâlâ çalıştığına bakar | |
| 7. Emekliye ayırma | Eski skilleri `~/.claude/skills-archive/` altına taşır | **sen** izin verirsin |

Her parça beş karardan birini alır: **keep** (aynen taşı), **merge** (birleştir), **update** (eski ama hâlâ lazım, sürüm notuyla taşı), **conflict** (sana sorulur) ya da **drop** (gerekçesiyle at). Her satırın bir kararı olmadan birleştirme bitmiş sayılmaz. İş bitince kayıt dosyası eski skillerin yanına, arşive gider. Ne olduğunu her zaman görebilirsin.

## Yardımcı script

`scripts/skills.py` tek başına da işe yarar:

```bash
python3 scripts/skills.py inventory            # kurulu bütün skiller, kelime sayılarıyla
python3 scripts/skills.py overlap              # birbirine benzeyen gruplar
python3 scripts/skills.py check path/to/skill  # frontmatter, ad, açıklama uzunluğu, kırık linkler
```

`overlap` sadece açıklamalardaki kelimeleri karşılaştırır, ilk tahmin gibi düşün. Ajan sana bir şey önermeden önce açıklamaları kendisi okur.

## Güvenlik

- Hiçbir şeyi silmez. Eski skiller `~/.claude/skills-archive/<tarih>-<ad>/` altına taşınır, geri taşımak birleştirmeyi geri alır.
- Yeni skill denetimden geçip sen onay vermeden kaynak klasörlere dokunmaz.
- Plugin skillerini düzenlemez, çünkü bir sonraki güncelleme üstüne yazar. İçerikleri yeni skill'e kopyalanır, plugin'i kapatıp kapatmamaya sen karar verirsin.
- skills CLI ile kurulmuş skilleri `npx skills remove` ile kaldırır. Böylece geride kırık link ya da kilit dosyası kaydı kalmaz.
- Lisanssız ya da başkasının lisansıyla gelen içeriği `SOURCES.md`'ye yazar, gerekiyorsa birleşen skill'i "sadece kişisel kullanım" diye işaretler.

## Katkı

Hata bildirimi ve PR'lar açık. Ayrıntılar [CONTRIBUTING.md](CONTRIBUTING.md)'de, değişiklikler [CHANGELOG.md](CHANGELOG.md)'de.

## Lisans

[MIT](LICENSE) © 2026 Rızgar Ozan
