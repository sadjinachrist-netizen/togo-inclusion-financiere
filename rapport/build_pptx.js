// Rapport Défi 2 — Mobile money et inclusion financière au Togo
// Génère Rapport_Defi2_Inclusion_Financiere_Togo.pptx (10 slides)

const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const OUT = path.join(__dirname, "Rapport_Defi2_Inclusion_Financiere_Togo.pptx");
const CAP = (n) => { const p = path.join(__dirname, "captures", n); return fs.existsSync(p) ? p : null; };
const URL = "togo-inclusion-financiere.streamlit.app";

const C = { dark: "0B3D2E", green: "0F6E4E", lime: "4ADE80", gold: "D9A521", red: "C8453B", ink: "14201A",
            muted: "5F6B66", card: "E8F1EC", redl: "FBEAEA", goldl: "FBF3DD", white: "FFFFFF" };
const HF = "Cambria", BF = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "SADJINA Christ";
pres.title = "Mobile money et inclusion financière au Togo — Défi 2";

// ---------------------------------------------------------------- helpers
const title = (s, t, o = {}) => s.addText(t, { x: 0.5, y: 0.32, w: 9, h: 0.7, fontFace: HF, fontSize: 26, bold: true, color: o.color || C.dark, isTextBox: true, margin: 0, valign: "middle" });
const kicker = (s, t, o = {}) => s.addText(t, { x: 0.5, y: 1.0, w: 9, h: 0.35, fontFace: BF, fontSize: 12.5, italic: true, color: o.color || C.muted, isTextBox: true, margin: 0, valign: "middle" });
const footer = (s, n, dark = false) => s.addText(`Défi 2 · Mobile money et inclusion financière au Togo  ·  SADJINA Christ  ·  ${n} / 10`, { x: 0.5, y: 5.22, w: 9, h: 0.25, fontFace: BF, fontSize: 9, color: dark ? "9FB8AC" : C.muted, isTextBox: true, margin: 0, align: "right" });
const card = (s, x, y, w, h, fill = C.card) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: fill, width: 0 }, rectRadius: 0.08 });
function stat(s, x, y, w, h, v, l, color = C.dark, fill = C.card, fs = 30) {
  card(s, x, y, w, h, fill);
  s.addText(v, { x: x + 0.15, y: y + 0.1, w: w - 0.3, h: h * 0.52, fontFace: HF, fontSize: fs, bold: true, color, isTextBox: true, margin: 0, valign: "middle" });
  s.addText(l, { x: x + 0.15, y: y + h * 0.6, w: w - 0.3, h: h * 0.38, fontFace: BF, fontSize: 10.5, color: C.muted, isTextBox: true, margin: 0, valign: "top" });
}
function box(s, x, y, w, h, head, body, fill = C.card, headColor = C.dark, bfs = 10.5) {
  card(s, x, y, w, h, fill);
  s.addText([{ text: head, options: { bold: true, color: headColor, fontSize: 12, breakLine: true } }, { text: body, options: { color: C.ink, fontSize: bfs } }],
    { x: x + 0.15, y: y + 0.08, w: w - 0.3, h: h - 0.16, fontFace: BF, isTextBox: true, margin: 0, valign: "top" });
}
function numbered(s, x, y, w, n, head, body, color = C.green) {
  s.addShape(pres.shapes.OVAL, { x, y: y + 0.03, w: 0.4, h: 0.4, fill: { color }, line: { color, width: 0 } });
  s.addText(String(n), { x, y: y + 0.03, w: 0.4, h: 0.4, fontFace: HF, fontSize: 15, bold: true, color: C.white, isTextBox: true, margin: 0, align: "center", valign: "middle" });
  s.addText([{ text: head, options: { bold: true, color: C.ink, fontSize: 12, breakLine: true } }, { text: body, options: { color: C.muted, fontSize: 10 } }],
    { x: x + 0.52, y, w: w - 0.52, h: 0.68, fontFace: BF, isTextBox: true, margin: 0, valign: "top" });
}
function image(s, file, x, y, w, h, label) {
  const p = CAP(file);
  if (p) { s.addImage({ path: p, x, y, w, h }); s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: C.white, transparency: 100 }, line: { color: "C9D6CE", width: 0.75 } }); }
  else { card(s, x, y, w, h, "DCE7E0"); s.addText(label, { x, y, w, h, fontFace: BF, fontSize: 12, color: C.muted, italic: true, isTextBox: true, align: "center", valign: "middle" }); }
}
const chartBase = { showLegend: false, catAxisLabelColor: C.ink, valAxisLabelColor: C.muted, valGridLine: { color: "E3E8E5", size: 0.5 }, catGridLine: { style: "none" }, catAxisLabelFontSize: 10, valAxisLabelFontSize: 9, dataLabelColor: C.ink, dataLabelFontSize: 9 };

// ================================================================ 1 · Titre
{
  const s = pres.addSlide(); s.background = { color: C.dark };
  s.addText("DATA CHALLENGE · ÉCONOMIE NUMÉRIQUE · DÉFI 2", { x: 0.6, y: 0.5, w: 8.8, h: 0.35, fontFace: BF, fontSize: 12, color: C.lime, bold: true, charSpacing: 2, isTextBox: true, margin: 0 });
  s.addText("Le mobile money, première porte d'entrée vers les services financiers", { x: 0.6, y: 0.95, w: 6.3, h: 1.75, fontFace: HF, fontSize: 32, bold: true, color: C.white, isTextBox: true, margin: 0, valign: "middle" });
  s.addText("Adoption du numérique et inclusion financière au Togo : usage d'Internet, marché télécom, établissements financiers, agents mobile money et population 2022, préfecture par préfecture.", { x: 0.6, y: 2.85, w: 6.1, h: 0.9, fontFace: BF, fontSize: 14, color: "CFE3D8", isTextBox: true, margin: 0, valign: "top" });
  s.addText([{ text: "Dashboard interactif en ligne : ", options: { color: "9FB8AC", fontSize: 12 } }, { text: URL, options: { color: C.lime, fontSize: 13, bold: true, hyperlink: { url: "https://" + URL } } }],
    { x: 0.6, y: 3.75, w: 6.2, h: 0.35, fontFace: BF, isTextBox: true, margin: 0 });
  s.addText([{ text: "SADJINA Christ", options: { bold: true, color: C.white, fontSize: 14, breakLine: true } }, { text: "Python · Streamlit · Plotly · 6 pages interactives · septembre 2026", options: { color: "9FB8AC", fontSize: 11 } }],
    { x: 0.6, y: 4.35, w: 6, h: 0.65, fontFace: BF, isTextBox: true, margin: 0, valign: "bottom" });
  [["19 788", "agents mobile money"], ["660", "établissements financiers actifs"], ["246 / 373", "cantons desservis par le seul mobile money", C.lime]].forEach(([v, l, col], i) => {
    const y = 1.0 + i * 1.25;
    s.addText(v, { x: 7.0, y, w: 2.5, h: 0.7, fontFace: HF, fontSize: 32, bold: true, color: col || C.white, isTextBox: true, margin: 0, align: "right", valign: "middle" });
    s.addText(l, { x: 6.6, y: y + 0.68, w: 2.9, h: 0.42, fontFace: BF, fontSize: 10.5, color: "9FB8AC", isTextBox: true, margin: 0, align: "right" });
  });
  s.addNotes("Le défi : mesurer l'adoption du numérique et le rôle du mobile money dans l'inclusion financière, puis recommander où accélérer. Le dashboard en ligne est le livrable principal ; ce rapport en résume les résultats.");
}

// ================================================================ 2 · Problème et données
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Le problème et les données mobilisées");
  kicker(s, "Le mobile est dans toutes les poches, Internet chez moins de 4 personnes sur 10, et les banques restent en ville.");
  s.addText("Cinq objectifs du défi", { x: 0.5, y: 1.45, w: 4.3, h: 0.3, fontFace: BF, fontSize: 12.5, bold: true, color: C.green, isTextBox: true, margin: 0 });
  const objs = ["Retracer l'évolution de l'usage d'Internet et ses périodes d'accélération", "Analyser le marché télécom : parts de marché, CA, investissements, 3G/4G/fibre",
    "Cartographier établissements financiers et agents mobile money", "Rapporter les points d'accès à la population : habitants par point de service, territoires desservis uniquement par le mobile money", "Recommander où accélérer Internet et l'inclusion financière"];
  s.addText(objs.map((t, i) => ({ text: t, options: { bullet: { code: "25A0" }, breakLine: i < objs.length - 1, paraSpaceAfter: 5 } })), { x: 0.5, y: 1.78, w: 4.3, h: 2.5, fontFace: BF, fontSize: 11, color: C.ink, isTextBox: true, margin: 0, valign: "top" });
  box(s, 0.5, 4.25, 4.3, 0.88, "Angle retenu", "Confronter l'offre (guichets bancaires, microfinances, agents) à la population de chaque préfecture et commune, et identifier les territoires où l'agent mobile money est le seul service financier.", C.card, C.dark, 10);
  s.addText("Sept sources, six fournies par le défi", { x: 5.2, y: 1.45, w: 4.3, h: 0.3, fontFace: BF, fontSize: 12.5, bold: true, color: C.green, isTextBox: true, margin: 0 });
  const hdr = { bold: true, color: C.white, fill: { color: C.green }, fontSize: 9.5 };
  const rows = [[{ text: "Jeu de données", options: hdr }, { text: "Contenu", options: hdr }, { text: "Période", options: hdr }],
    ["Agents mobile money", "19 788 points, région → canton", "déc. 2024"],
    ["Établissements financiers", "738 points : banques, microfinances, assurances", "janv. 2025"],
    ["Population RGPH-5", "759 unités, hiérarchie aplatie", "2022"],
    ["Usage d'Internet (Banque mondiale)", "% d'individus utilisant Internet", "1960-2022"],
    ["Abonnés Internet (ARCEP)", "25 indicateurs par techno et opérateur", "2013-2019"],
    ["Marché téléphonie (ARCEP)", "abonnés, CA, investissements, parts", "2013-2019"],
    [{ text: "Contours (geoBoundaries)", options: { italic: true } }, { text: "5 régions, 37 préfectures — source externe", options: { italic: true } }, { text: "2017", options: { italic: true } }]];
  s.addTable(rows, { x: 5.2, y: 1.78, w: 4.3, colW: [1.7, 1.9, 0.7], fontFace: BF, fontSize: 8.5, color: C.ink, border: { type: "solid", color: "D5E0DA", pt: 0.5 }, rowH: 0.27, margin: [0.02, 0.05, 0.02, 0.05], valign: "middle" });
  box(s, 5.2, 4.25, 4.3, 0.88, "Maille d'analyse", "6 régions (Grand Lomé distinct, comme dans le RGPH-5) · 39 préfectures · 117 communes · 373 cantons. Population disponible jusqu'à la commune.", C.card, C.dark, 10);
  footer(s, 2);
  s.addNotes("Le Géoportail ne fournit pas de limites de préfecture : les contours viennent de geoBoundaries (OpenStreetMap), en licence ouverte, avec fusion documentée des trois préfectures créées après 2017.");
}

// ================================================================ 3 · Six chiffres
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Le diagnostic en six chiffres");
  kicker(s, "L'accès financier existe presque partout — mais, hors des villes, il se réduit à l'agent mobile money.");
  const items = [["37,6 %", "des Togolais utilisent Internet en 2022 — 0,8 % en 2000, 4,5 % en 2013", C.dark],
    ["409", "habitants par agent mobile money, contre 12 266 par établissement financier et 38 007 par banque", C.dark],
    ["33,5", "agents mobile money pour un guichet de banque ou de microfinance ; 49,6 dans les Savanes", C.dark],
    ["246 / 373", "cantons (66 %) sans aucun établissement financier : l'agent mobile money y est le seul guichet", C.red],
    ["9 / 39", "préfectures sans aucune banque ; Kpendjal n'a aucun établissement financier", C.red],
    ["40 %", "des établissements financiers sont dans le Grand Lomé, pour 27 % de la population", C.red]];
  items.forEach(([v, l, col], i) => stat(s, 0.5 + (i % 3) * 3.1, 1.5 + Math.floor(i / 3) * 1.8, 2.9, 1.6, v, l, col, col === C.red ? C.redl : C.card));
  footer(s, 3);
  s.addNotes("Chiffres calculés sur les établissements en activité (660 sur 738) et la population RGPH-5 2022. Un guichet = banque ou microfinance.");
}

// ================================================================ 4 · Méthodologie
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Méthodologie : un pipeline reproductible");
  kicker(s, "Un pipeline Python unique reconstruit toutes les tables ; chaque correction est documentée dans l'application.");
  const steps = [["Fiabilisation", "Parsing des géométries WKT · statuts d'activité harmonisés (14 valeurs → 4) · opérateurs multi-valués éclatés · anciens noms d'opérateurs relabellisés."],
    ["Population", "Hiérarchie reconstruite à partir d'un fichier sans colonne de niveau, validée par « préfecture = somme des communes ». Avé reconstruite, deux libellés dupliqués réaffectés, Binah 2 imputée."],
    ["Indicateurs", "Par région, préfecture, commune et canton : habitants par établissement, par banque, par agent ; agents pour 1 000 hab. ; agents par guichet ; profil des cantons."],
    ["Restitution", "Streamlit + Plotly, déployé en ligne : 6 pages, choroplèthes sur vrais contours, filtres, survols, exports CSV, page méthodologie et limites."]];
  steps.forEach(([h, b], i) => { const x = 0.5 + i * 2.3; card(s, x, 1.5, 2.15, 2.65);
    s.addShape(pres.shapes.OVAL, { x: x + 0.15, y: 1.65, w: 0.42, h: 0.42, fill: { color: C.green }, line: { color: C.green, width: 0 } });
    s.addText(String(i + 1), { x: x + 0.15, y: 1.65, w: 0.42, h: 0.42, fontFace: HF, fontSize: 15, bold: true, color: C.white, isTextBox: true, margin: 0, align: "center", valign: "middle" });
    s.addText(h, { x: x + 0.67, y: 1.65, w: 1.4, h: 0.42, fontFace: BF, fontSize: 13.5, bold: true, color: C.dark, isTextBox: true, margin: 0, valign: "middle" });
    s.addText(b, { x: x + 0.15, y: 2.18, w: 1.85, h: 1.9, fontFace: BF, fontSize: 10, color: C.ink, isTextBox: true, margin: 0, valign: "top" }); });
  box(s, 0.5, 4.3, 9.0, 0.8, "Deux choix assumés", "Six régions, le Grand Lomé étant publié hors Maritime dans le RGPH-5 — le traiter comme une région fait apparaître la concentration réelle. Un canton est « mobile money uniquement » s'il compte au moins un agent et aucun établissement financier en activité : c'est un indicateur d'accès physique, pas d'usage.", C.goldl, "8A6510", 10);
  footer(s, 4);
  s.addNotes("Toutes les étapes sont dans pipeline/build_data.py, livré dans l'archive avec les données brutes.");
}

// ================================================================ 5 · Internet
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Internet : stagnation, puis accélération");
  kicker(s, "Part des individus utilisant Internet (Banque mondiale) et lecture par phases.");
  const years = ["2000", "2002", "2004", "2006", "2008", "2010", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022"];
  const vals = [0.8, 1.0, 1.5, 2.0, 2.4, 3.0, 4.0, 4.5, 5.7, 7.1, 11.3, 12.4, 15.5, 20.7, 29.0, 32.5, 37.6];
  s.addChart(pres.charts.LINE, [{ name: "% individus", labels: years, values: vals }], { ...chartBase, x: 0.5, y: 1.45, w: 5.7, h: 3.65, chartColors: [C.green], lineSize: 3, lineDataSymbolSize: 6,
    showValue: true, dataLabelPosition: "t", dataLabelFormatCode: "0.0", showTitle: true, title: "Individus utilisant Internet (% de la population)", titleFontSize: 11, titleColor: C.dark, valAxisMaxVal: 45, valAxisMinVal: 0 });
  box(s, 6.45, 1.45, 3.05, 1.12, "2000-2013 · stagnation", "De 0,8 % à 4,5 % : +0,3 point par an. Internet est fixe, urbain, cher — moins de 65 000 abonnés fixes.", C.redl, C.red, 10);
  box(s, 6.45, 2.67, 3.05, 1.12, "2014-2019 · décollage mobile", "+16 points. La 3G passe de 130 000 à 1,9 million de clients, la 4G est lancée en 2018. Taux de pénétration ARCEP : 5 % → 50 %.", C.goldl, "8A6510", 10);
  box(s, 6.45, 3.89, 3.05, 1.2, "2020-2022 · accélération", "+17 points en trois ans, dont +8,3 en 2020. Les revenus du secteur restent à ~180 Md FCFA : le prix de l'accès s'effondre, l'usage suit l'utilité.", C.card, C.dark, 10);
  footer(s, 5);
  s.addNotes("Deux sources se complètent : l'ARCEP compte des abonnements (44,8 pour 100 habitants en 2019), la Banque mondiale des individus (20,7 % la même année). Les séries ARCEP s'arrêtent en 2019.");
}

// ================================================================ 6 · Concentration régionale
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "L'offre financière ne suit pas la population");
  kicker(s, "Part nationale de chaque région dans la population, les établissements financiers et les agents mobile money.");
  const regs = ["Grand Lomé", "Maritime", "Plateaux", "Centrale", "Kara", "Savanes"];
  s.addChart(pres.charts.BAR, [
    { name: "Population", labels: regs, values: [27.0, 16.6, 20.2, 9.8, 12.2, 14.1] },
    { name: "Établissements financiers", labels: regs, values: [40.3, 14.8, 15.3, 9.4, 12.0, 8.2] },
    { name: "Agents mobile money", labels: regs, values: [32.9, 12.5, 15.6, 10.6, 14.9, 13.5] },
  ], { ...chartBase, x: 0.5, y: 1.45, w: 5.6, h: 3.6, barDir: "col", barGrouping: "clustered", chartColors: ["9FB8AC", C.dark, C.red], showLegend: true, legendPos: "t", legendFontSize: 10,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0", valAxisMaxVal: 45, valAxisMinVal: 0, valAxisTitle: "Part nationale (%)", showValAxisTitle: true, valAxisTitleFontSize: 9 });
  const hdr = { bold: true, color: C.white, fill: { color: C.green }, fontSize: 9.5 };
  s.addTable([[{ text: "Région", options: hdr }, { text: "Hab. / étab.", options: { ...hdr, align: "right" } }, { text: "Agents / guichet", options: { ...hdr, align: "right" } }],
    ["Grand Lomé", { text: "8 227", options: { align: "right" } }, { text: "31,0", options: { align: "right" } }],
    ["Kara", { text: "12 475", options: { align: "right" } }, { text: "41,0", options: { align: "right" } }],
    ["Centrale", { text: "12 831", options: { align: "right" } }, { text: "33,8", options: { align: "right" } }],
    ["Maritime", { text: "13 741", options: { align: "right" } }, { text: "26,2", options: { align: "right" } }],
    ["Plateaux", { text: "16 197", options: { align: "right" } }, { text: "31,4", options: { align: "right" } }],
    ["Savanes", { text: "21 176", options: { align: "right", color: C.red, bold: true } }, { text: "49,6", options: { align: "right", color: C.red, bold: true } }]],
    { x: 6.35, y: 1.45, w: 3.15, colW: [1.25, 0.95, 0.95], fontFace: BF, fontSize: 10, color: C.ink, border: { type: "solid", color: "D5E0DA", pt: 0.5 }, rowH: 0.29, valign: "middle" });
  box(s, 6.35, 3.6, 3.15, 1.5, "Lecture", "Le Grand Lomé concentre 40 % des établissements pour 27 % de la population. Dans les Savanes, un établissement dessert 21 176 habitants — 2,6 fois plus qu'à Lomé — et un guichet « couvre » 50 agents mobile money : le mobile money y remplace la banque.", C.redl, C.red, 9.5);
  footer(s, 6);
  s.addNotes("Les Plateaux, deuxième région la plus peuplée (20 %), ne reçoivent que 15 % des établissements et 16 % des agents — la région la moins dotée en agents pour 1 000 habitants (1,88 contre 2,44).");
}

// ================================================================ 7 · Carte
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Neuf préfectures sans banque");
  kicker(s, "Habitants par établissement financier (teinte) et banques en activité (points) — page « Carte des services » du dashboard.");
  image(s, "carte_map.png", 0.5, 1.45, 2.85, 3.7, "Capture — carte");
  const hdr = { bold: true, color: C.white, fill: { color: C.red }, fontSize: 9.5 };
  const rows = [[{ text: "Préfecture sans banque", options: hdr }, { text: "Région", options: hdr }, { text: "Habitants", options: { ...hdr, align: "right" } }, { text: "Étab.", options: { ...hdr, align: "right" } }, { text: "Agents MM", options: { ...hdr, align: "right" } }]];
  [["Est-Mono", "Plateaux", "164 460", "3", "209"], ["Kpendjal-Ouest", "Savanes", "123 330", "3", "129"], ["Amou", "Plateaux", "114 172", "6", "175"], ["Bas-Mono", "Maritime", "94 860", "4", "183"],
   ["Moyen-Mono", "Plateaux", "90 505", "5", "81"], ["Kpendjal", "Savanes", "88 365", "0", "41"], ["Akébou", "Plateaux", "73 830", "1", "87"], ["Mô", "Centrale", "52 448", "2", "32"], ["Danyi", "Plateaux", "40 240", "3", "142"]]
    .forEach(r => rows.push([{ text: r[0], options: { bold: r[0] === "Kpendjal" } }, r[1], { text: r[2], options: { align: "right" } }, { text: r[3], options: { align: "right", color: r[3] === "0" ? C.red : C.ink, bold: r[3] === "0" } }, { text: r[4], options: { align: "right" } }]));
  s.addTable(rows, { x: 3.55, y: 1.45, w: 5.95, colW: [1.55, 1.0, 1.1, 0.7, 1.6], fontFace: BF, fontSize: 9.5, color: C.ink, border: { type: "solid", color: "EAD3D3", pt: 0.5 }, rowH: 0.255, valign: "middle" });
  box(s, 3.55, 4.15, 5.95, 0.95, "842 210 habitants sans banque dans leur préfecture", "Kpendjal (88 365 habitants) n'a aucun établissement financier et 41 agents mobile money — 0,46 pour 1 000 habitants, cinq fois moins que la moyenne nationale : c'est le territoire le plus à l'écart du pays. Akébou compte 73 830 habitants pour un seul établissement.", C.redl, C.red, 9.5);
  footer(s, 7);
  s.addNotes("La carte est interactive dans le dashboard : 8 indicateurs, maille région ou préfecture, superposition des banques, microfinances, assurances et des 19 788 agents mobile money.");
}

// ================================================================ 8 · Mobile money uniquement
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Deux cantons sur trois n'ont que le mobile money");
  kicker(s, "Profil des 373 cantons et préfectures comptant le plus de cantons desservis uniquement par le mobile money.");
  s.addChart(pres.charts.DOUGHNUT, [{ name: "Cantons", labels: ["Mobile money uniquement", "Mobile money + établissements"], values: [246, 127] }],
    { x: 0.5, y: 1.45, w: 3.3, h: 3.0, chartColors: [C.red, C.green], holeSize: 60, showLegend: true, legendPos: "b", legendFontSize: 9, showValue: true, showPercent: true, dataLabelColor: C.white, dataLabelFontSize: 11, dataLabelFontBold: true, showTitle: true, title: "373 cantons", titleFontSize: 11, titleColor: C.dark });
  const prefs = ["Tône", "Kozah", "Tchaoudjo", "Dankpen", "Wawa", "Kloto", "Tandjoaré", "Agou", "Blitta", "Amou"];
  s.addChart(pres.charts.BAR, [{ name: "MM uniquement", labels: prefs, values: [16, 13, 11, 11, 11, 10, 10, 10, 8, 8] }, { name: "Autres cantons", labels: prefs, values: [2, 2, 2, 1, 2, 4, 3, 3, 3, 3] }],
    { ...chartBase, x: 3.95, y: 1.45, w: 5.55, h: 3.0, barDir: "col", barGrouping: "stacked", chartColors: [C.red, "D5E0DA"], showLegend: true, legendPos: "b", legendFontSize: 9, showValue: false, valAxisTitle: "Cantons", showValAxisTitle: true, valAxisTitleFontSize: 9, showTitle: true, title: "Préfectures comptant le plus de cantons « mobile money uniquement »", titleFontSize: 11, titleColor: C.dark });
  box(s, 0.5, 4.55, 4.4, 0.55, "3 373 agents mobile money", "sont le seul service financier de leur canton (17 % des agents).", C.redl, C.red, 10);
  box(s, 5.1, 4.55, 4.4, 0.55, "Plateaux : 74 cantons sur 110 · Kara : 58 sur 72", "22 communes sur 117 sont dans le même cas.", C.card, C.dark, 10);
  footer(s, 8);
  s.addNotes("Ces territoires ne sont pas des zones blanches : le service existe, mais il se limite au dépôt, au retrait et au transfert. Ni épargne rémunérée, ni crédit, ni assurance.");
}

// ================================================================ 9 · Recommandations
{
  const s = pres.addSlide(); s.background = { color: C.white };
  title(s, "Six recommandations chiffrées et territorialisées");
  kicker(s, "Chacune est rattachée à un nombre d'habitants concernés et à des préfectures nommées.");
  const recs = [["Faire des agents mobile money des guichets financiers complets", "3 373 agents dans 246 cantons sans établissement : épargne, micro-crédit, micro-assurance et paiements publics via partenariats banques / microfinances / opérateurs, avec formation certifiante. Priorité : Plateaux (74 cantons), Kara (58).", C.red],
    ["Ouvrir un guichet de microfinance dans les 9 préfectures sans banque", "842 210 habitants. Kpendjal d'abord (0 établissement), puis Est-Mono, Kpendjal-Ouest, Amou. Cible : un guichet par chef-lieu en 24 mois, adossé à un super-agent mobile money.", C.red],
    ["Rattraper les 9 préfectures à plus de deux fois la moyenne nationale", "+15 établissements pour ramener chacune sous 24 500 habitants par point de service : Est-Mono +4, Akébou +2, Kpendjal-Ouest +2, Dankpen +2, et +1 pour Oti-Sud, Tandjoaré, Mô, Tône, Wawa.", C.red],
    ["Rééquilibrer Plateaux et Savanes", "34 % de la population, 23 % des établissements. Densifier les agents dans les Plateaux (1,88 pour 1 000 hab.), les guichets dans les Savanes (49,6 agents par guichet).", C.green],
    ["Porter l'usage d'Internet de 37,6 % à 50 %", "1 million de personnes à connecter. La télédensité plafonne à 82 % : jouer sur la 4G hors Lomé, les forfaits data d'entrée de gamme et les services publics numériques.", C.green],
    ["Compléter l'open data", "Séries ARCEP après 2019, opérateur des 6,8 % d'agents non renseignés, hiérarchie et niveaux dans le fichier population, contours des préfectures récentes.", C.green]];
  recs.forEach(([h, b, col], i) => numbered(s, 0.5 + (i % 2) * 4.6, 1.45 + Math.floor(i / 2) * 1.22, 4.4, i + 1, h, b, col));
  footer(s, 9);
  s.addNotes("L'indice de priorité du dashboard (50 % habitants par établissement, 25 % agents pour 1 000 habitants inversé, 25 % part de cantons MM uniquement) classe Kpendjal, Akébou, Est-Mono, Kpendjal-Ouest et Dankpen en tête.");
}

// ================================================================ 10 · Limites et livrable
{
  const s = pres.addSlide(); s.background = { color: C.dark };
  title(s, "Limites, perspectives et livrable", { color: C.white });
  kicker(s, "Ce que ces données ne disent pas encore — et ce que le dashboard permet de faire dès maintenant.", { color: "9FB8AC" });
  s.addText("Limites", { x: 0.5, y: 1.45, w: 2.9, h: 0.3, fontFace: BF, fontSize: 12.5, bold: true, color: C.lime, isTextBox: true, margin: 0 });
  const lim = ["Le nombre d'agents mesure l'accès physique, pas les transactions ni les comptes actifs.", "Aucune donnée d'usage d'Internet infranationale : la fracture territoriale n'est approchée que par les points de service.", "Séries ARCEP arrêtées en 2019 ; points de 2024-2025 rapportés à la population 2022.", "Contours 2017 : trois préfectures récentes fusionnées avec leur préfecture d'origine sur la carte."];
  s.addText(lim.map((t, i) => ({ text: t, options: { bullet: { code: "25A0" }, breakLine: i < lim.length - 1, paraSpaceAfter: 6 } })), { x: 0.5, y: 1.78, w: 2.9, h: 2.7, fontFace: BF, fontSize: 10, color: "DCE9E1", isTextBox: true, margin: 0, valign: "top" });
  s.addText("Perspectives", { x: 3.65, y: 1.45, w: 2.7, h: 0.3, fontFace: BF, fontSize: 12.5, bold: true, color: C.lime, isTextBox: true, margin: 0 });
  const per = ["Croiser avec les volumes de transactions mobile money (BCEAO) pour passer de l'accès à l'usage.", "Calculer la distance de chaque canton au guichet le plus proche.", "Suivre l'indice de priorité chaque année à partir du même pipeline."];
  s.addText(per.map((t, i) => ({ text: t, options: { bullet: { code: "25A0" }, breakLine: i < per.length - 1, paraSpaceAfter: 6 } })), { x: 3.65, y: 1.78, w: 2.7, h: 2.7, fontFace: BF, fontSize: 10, color: "DCE9E1", isTextBox: true, margin: 0, valign: "top" });
  s.addText("Le dashboard", { x: 6.6, y: 1.45, w: 2.9, h: 0.3, fontFace: BF, fontSize: 12.5, bold: true, color: C.lime, isTextBox: true, margin: 0 });
  image(s, "vue.png", 6.6, 1.78, 2.9, 1.7, "Capture — vue d'ensemble");
  s.addText([{ text: "6 pages · choroplèthes · filtres · exports CSV · méthodologie intégrée", options: { color: "DCE9E1", fontSize: 10, breakLine: true } },
    { text: "https://" + URL, options: { color: C.lime, fontSize: 11, bold: true, hyperlink: { url: "https://" + URL }, breakLine: true } },
    { text: "Code, données brutes et pipeline dans l'archive jointe.", options: { color: "9FB8AC", fontSize: 9.5, italic: true } }], { x: 6.6, y: 3.55, w: 2.9, h: 1.0, fontFace: BF, isTextBox: true, margin: 0, valign: "top" });
  s.addText("L'inclusion financière est déjà là, dans la poche. Il reste à lui donner un guichet.", { x: 0.5, y: 4.6, w: 9, h: 0.5, fontFace: HF, fontSize: 17, bold: true, italic: true, color: C.white, isTextBox: true, margin: 0, valign: "middle" });
  footer(s, 10, true);
  s.addNotes("Conclusion. Les limites sont des lacunes de l'open data, retournées en recommandation n°6.");
}

pres.writeFile({ fileName: OUT }).then(() => console.log("OK ->", OUT));
