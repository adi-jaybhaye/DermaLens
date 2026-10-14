"""
Structured registry of scientific research sources supporting DermaLens XAI explanations.

Every source in this registry corresponds to an actual inspected document in
backend/data/research/. All author names, publication years, identifiers (DOI/PMID/URL),
findings, and limitations are directly extracted from the original document contents.

NO FABRICATED CITATIONS. NO IMAGINED FINDINGS.
"""

from typing import Optional, TypedDict


class EvidenceSource(TypedDict):
    id: str
    file_name: str
    title: str
    authors: str
    year: str
    source_type: str
    authority: str
    identifier: str
    url: Optional[str]
    topic: str
    key_findings: str
    limitations: str
    supported_claims: list[str]
    unsupported_claims: list[str]


EVIDENCE_SOURCES: dict[str, EvidenceSource] = {
    "SRC-01": {
        "id": "SRC-01",
        "file_name": "01.docx",
        "title": "Anatomy, Skin (Integument)",
        "authors": "StatPearls Publishing / NCBI Bookshelf",
        "year": "2026",
        "source_type": "Clinical anatomical reference",
        "authority": "NCBI Bookshelf / StatPearls",
        "identifier": "PMID: 28723009; NBK441980",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK441980/",
        "topic": "Cutaneous anatomy and microvasculature",
        "key_findings": (
            "The skin comprises epidermis and dermis with a rich vascular network. "
            "Dermal capillary loops regulate thermoregulation and local tissue perfusion."
        ),
        "limitations": (
            "Anatomical description only; does not validate automated camera-based "
            "skin feature extraction or clinical disease classification."
        ),
        "supported_claims": [
            "Dermal blood vessels regulate skin perfusion and temperature",
            "Superficial vasculature contributes to visible skin coloration",
        ],
        "unsupported_claims": [
            "Camera images can measure capillary blood flow directly",
            "Visible redness is proof of a specific internal pathology",
        ],
    },
    "SRC-02": {
        "id": "SRC-02",
        "file_name": "02.docx",
        "title": "Physiology, Integument",
        "authors": "StatPearls Publishing / NCBI Bookshelf",
        "year": "2020",
        "source_type": "Clinical physiology reference",
        "authority": "NCBI Bookshelf / StatPearls",
        "identifier": "PMID: 32119273; NBK554386",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK554386/",
        "topic": "Cutaneous physiological regulation and vasodilation",
        "key_findings": (
            "Cutaneous blood flow changes dynamically via vasodilation in response to "
            "temperature, autonomic signaling, and inflammatory mediators."
        ),
        "limitations": (
            "Physiology reference; does not prove photographic detection of specific underlying disease."
        ),
        "supported_claims": [
            "Vasodilation increases surface blood flow and produces visible redness",
            "Redness can occur through non-pathological environmental and autonomic triggers",
        ],
        "unsupported_claims": [
            "2D images can determine internal endothelial or hormonal mechanisms",
        ],
    },
    "SRC-03": {
        "id": "SRC-03",
        "file_name": "03.docx",
        "title": "Anatomy, Skin (Integument), Epidermis",
        "authors": "StatPearls Publishing / NCBI Bookshelf",
        "year": "2019",
        "source_type": "Histology reference",
        "authority": "NCBI Bookshelf / StatPearls",
        "identifier": "PMID: 30726010; NBK537325",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK537325/",
        "topic": "Epidermal strata, melanocytes, and keratinocyte maturation",
        "key_findings": (
            "The epidermis consists of stratified squamous epithelium with 5 strata. "
            "Melanocytes reside in the Stratum Basale, synthesizing melanin that is packaged "
            "into melanosomes and transferred to keratinocytes."
        ),
        "limitations": (
            "Histological reference; 2D surface photography cannot evaluate microscopic "
            "cellular layers or histological pigment depth."
        ),
        "supported_claims": [
            "Melanin produced by basal melanocytes is the primary determinant of skin pigmentation",
            "Keratinocytes carry melanin outward through epidermal turnover",
        ],
        "unsupported_claims": [
            "Surface cameras can distinguish epidermal from dermal melanocytosis depth",
        ],
    },
    "SRC-04": {
        "id": "SRC-04",
        "file_name": "04.docx",
        "title": "Anatomy, Skin Appendages",
        "authors": "StatPearls Publishing / NCBI Bookshelf",
        "year": "2018",
        "source_type": "Anatomical reference",
        "authority": "NCBI Bookshelf / StatPearls",
        "identifier": "PMID: 29489291; NBK482237",
        "url": "https://www.ncbi.nlm.nih.gov/books/NBK482237/",
        "topic": "Pilosebaceous unit, hair follicle, and sebaceous gland architecture",
        "key_findings": (
            "Pilosebaceous units consist of hair follicles, sebaceous glands, and arrector pili. "
            "Sebaceous glands secrete sebum through the follicular canal to the skin surface."
        ),
        "limitations": (
            "Gross and microscopic anatomy; does not validate camera-based sebum quantification."
        ),
        "supported_claims": [
            "Sebum exits to the skin surface through the follicular opening (pore)",
            "Follicular structure forms the anatomical site for comedones and acne lesions",
        ],
        "unsupported_claims": [
            "Pore visibility on a camera directly equates to sebaceous gland volume",
        ],
    },
    "SRC-05": {
        "id": "SRC-05",
        "file_name": "05.docx",
        "title": "Evaluation of facial skin type by sebum secretion: discrepancies between subjective descriptions and sebum secretion",
        "authors": "Sang Woong Youn, Soo Jung Kim, In A Hwang, Kyoung Chan Park",
        "year": "2002",
        "source_type": "Primary clinical research",
        "authority": "Skin Research and Technology / Wiley",
        "identifier": "DOI: 10.1034/j.1600-0846.2002.10320.x; PMID: 12236886",
        "url": "https://pubmed.ncbi.nlm.nih.gov/12236886/",
        "topic": "Sebum secretion measurement and skin type discrepancies",
        "key_findings": (
            "Subjective self-assessment of skin type does not correlate with physical sebum "
            "secretion measured by Sebumeter. Most individuals misclassify their sebum levels. "
            "Standardized, objective biophysical measurement tools are mandatory for skin typing."
        ),
        "limitations": (
            "Study evaluated Korean volunteers with instrumental Sebumeter contact measurements. "
            "Directly proves that visual/subjective assessment cannot determine skin type."
        ),
        "supported_claims": [
            "Visual appearance alone does not match physical sebum secretion",
            "Objective skin type classification requires physical biophysical instrumentation",
            "Camera-only assessment cannot determine physiological skin type",
        ],
        "unsupported_claims": [
            "Camera-based AI can determine whether skin is dry, oily, or combination",
        ],
    },
    "SRC-06": {
        "id": "SRC-06",
        "file_name": "06.docx",
        "title": "Regional and seasonal variations in facial sebum secretions: a proposal for the definition of combination skin type",
        "authors": "Sang Woong Youn, Jung Im Na, Sun Young Choi, Chang Hun Huh, Kyoung Chan Park",
        "year": "2005",
        "source_type": "Primary clinical research",
        "authority": "Skin Research and Technology / Wiley",
        "identifier": "DOI: 10.1111/j.1600-0846.2005.00119.x; PMID: 15998330",
        "url": "https://pubmed.ncbi.nlm.nih.gov/15998330/",
        "topic": "Regional (T-zone vs U-zone) and seasonal variations in sebum",
        "key_findings": (
            "Facial sebum secretion exhibits pronounced regional differences (forehead, nose, "
            "and chin secrete significantly more sebum than cheeks) and seasonal fluctuations "
            "(summer is highest, winter is lowest)."
        ),
        "limitations": (
            "Longitudinal study of 20 Korean volunteers using Sebumeter. Demonstrates that skin "
            "properties fluctuate and cannot be characterized by a single static visual snapshot."
        ),
        "supported_claims": [
            "Sebum secretion varies significantly between facial zones (T-zone vs cheeks)",
            "Sebum output shifts across seasons and environmental temperatures",
        ],
        "unsupported_claims": [
            "A single photograph captures static personal sebum biology",
        ],
    },
    "SRC-07": {
        "id": "SRC-07",
        "file_name": "07.docx",
        "title": "Clinical scoring and instrumental analysis to evaluate skin types",
        "authors": "D G Mercurio, J H Segura, M B A Demets, P M B G Maia Campos",
        "year": "2013",
        "source_type": "Primary clinical research",
        "authority": "Clinical and Experimental Dermatology / BAD",
        "identifier": "DOI: 10.1111/ced.12105; PMID: 23517362",
        "url": "https://pubmed.ncbi.nlm.nih.gov/23517362/",
        "topic": "Biophysical parameters (TEWL, capacitance, sebum) and skin typing",
        "key_findings": (
            "Objective characterization of skin types requires multi-instrumental biophysical "
            "evaluations: stratum corneum water content, transepidermal water loss (TEWL), "
            "sebum excretion, microrelief roughness, and surface pH."
        ),
        "limitations": (
            "Small cohort (26 volunteers); confirms that physical probe contact measurements "
            "are essential to characterize barrier function and hydration."
        ),
        "supported_claims": [
            "Skin type is defined by barrier function, water content, and oiliness together",
            "Instrumental measurements provide objective validation that simple observation cannot",
        ],
        "unsupported_claims": [
            "Consumer camera pixels can substitute for TEWL or corneometry probes",
        ],
    },
    "SRC-08": {
        "id": "SRC-08",
        "file_name": "08_Acne.docx",
        "title": "Acne: Causes, Types, and Breakout Presentations",
        "authors": "American Academy of Dermatology (AAD)",
        "year": "2024",
        "source_type": "Official clinical guidance",
        "authority": "American Academy of Dermatology (AAD)",
        "identifier": "AAD Clinical Guidance",
        "url": "https://www.aad.org/public/diseases/acne/causes/acne-causes",
        "topic": "Clinical acne lesions (comedones, papules, pustules, cysts)",
        "key_findings": (
            "Acne breakouts range from non-inflammatory comedones (blackheads and whiteheads) "
            "to inflammatory lesions (papules and pustules) and deep nodules/cysts. A blackhead "
            "darkens because trapped oil and keratin oxidize when exposed to air, not because of dirt."
        ),
        "limitations": (
            "Patient educational guidance; does not validate remote automated image diagnostics."
        ),
        "supported_claims": [
            "Blackheads (open comedones) appear dark due to oxidation with air, not dirt",
            "Whiteheads (closed comedones) are closed, skin-colored or pale uninflamed plugs",
            "Inflammatory acne lesions present with surrounding redness and swelling",
            "Picking and squeezing increases inflammation and risk of scarring",
        ],
        "unsupported_claims": [
            "AI visual analysis can determine internal hormonal causes of acne",
        ],
    },
    "SRC-09": {
        "id": "SRC-09",
        "file_name": "09_Pigmentation.docx",
        "title": "Melasma",
        "authors": "Amanda Oakley, Brent J Doolan, Monisha Gupta",
        "year": "2025",
        "source_type": "Official dermatology educational resource",
        "authority": "DermNet NZ",
        "identifier": "DermNet NZ Reference",
        "url": "https://dermnetnz.org/topics/melasma",
        "topic": "Facial hyperpigmentation, melasma, UV and hormonal factors",
        "key_findings": (
            "Melasma presents as bilateral, blotchy brownish facial pigmentation. "
            "It is triggered by ultraviolet radiation, visible light, hormonal fluctuations "
            "(pregnancy, oral contraceptives), and genetic predisposition."
        ),
        "limitations": (
            "Clinical review; photographic appearance cannot confirm histological depth "
            "(epidermal vs dermal) without Wood lamp or dermatoscopic examination."
        ),
        "supported_claims": [
            "Melasma appears as blotchy, brownish facial pigmentation",
            "Sun exposure and UV light are primary triggers for facial pigmentation",
            "Hormonal factors strongly influence pigmentary changes",
        ],
        "unsupported_claims": [
            "An RGB photo can differentiate epidermal from dermal melasma depth",
        ],
    },
    "SRC-10": {
        "id": "SRC-10",
        "file_name": "10_AcneScientific references.docx",
        "title": "Acne vulgaris",
        "authors": "Amanda Oakley, Vanessa Ngan, Chelsea Jones, Monisha Gupta",
        "year": "2021",
        "source_type": "Official dermatology educational resource",
        "authority": "DermNet NZ",
        "identifier": "DermNet NZ Reference",
        "url": "https://dermnetnz.org/topics/acne-vulgaris",
        "topic": "Acne vulgaris pathophysiology, morphology, and skin-of-color nuances",
        "key_findings": (
            "Acne vulgaris is an eruption of the pilosebaceous unit presenting with mixed "
            "inflammatory and non-inflammatory lesions. Lesions frequently leave temporary "
            "post-inflammatory erythema or hyperpigmentation, especially in skin of color."
        ),
        "limitations": (
            "Clinical taxonomy; lesion severity grading requires standardized physical clinical examination."
        ),
        "supported_claims": [
            "Acne affects pilosebaceous units across the face and upper trunk",
            "Acne lesions often leave temporary red or dark marks after healing",
        ],
        "unsupported_claims": [
            "Image pattern recognition substitutes for clinical acne grading scales",
        ],
    },
    "SRC-11": {
        "id": "SRC-11",
        "file_name": "11_Pigmentation  Dark Spots.docx",
        "title": "Postinflammatory hyperpigmentation",
        "authors": "Vanessa Ngan, Amanda Oakley",
        "year": "2015",
        "source_type": "Official dermatology educational resource",
        "authority": "DermNet NZ",
        "identifier": "DermNet NZ Reference",
        "url": "https://dermnetnz.org/topics/postinflammatory-hyperpigmentation",
        "topic": "Post-inflammatory hyperpigmentation (PIH) and localized dark spots",
        "key_findings": (
            "Post-inflammatory hyperpigmentation follows cutaneous injury or inflammatory disorders "
            "(such as acne or eczema). Inflammatory mediators stimulate melanocytes to increase "
            "melanin synthesis, depositing excess pigment in keratinocytes or dermal macrophages."
        ),
        "limitations": (
            "Clinical overview; visual observation cannot distinguish benign post-inflammatory "
            "pigment from atypical pigmented melanocytic lesions."
        ),
        "supported_claims": [
            "Dark spots frequently develop after blemishes, scratches, or inflammation heal",
            "Sun exposure darkens and prolongs post-inflammatory spots",
            "Melanin production increases in response to prior cutaneous inflammation",
        ],
        "unsupported_claims": [
            "The model can confirm whether a dark spot is benign or requires biopsy",
        ],
    },
    "SRC-12": {
        "id": "SRC-12",
        "file_name": "12_Facial Redness.docx",
        "title": "10 reasons your face is red",
        "authors": "American Academy of Dermatology (AAD)",
        "year": "2024",
        "source_type": "Official clinical guidance",
        "authority": "American Academy of Dermatology (AAD)",
        "identifier": "AAD Public Guidance",
        "url": "https://www.aad.org/public/everyday-care/skin-care-basics/care/face-is-red",
        "topic": "Etiological diversity and non-specificity of facial redness",
        "key_findings": (
            "Facial redness has numerous distinct causes, including seborrheic dermatitis, "
            "rosacea, contact allergies, temperature changes, sunburn, and medication reactions. "
            "Because redness is a non-specific sign, professional clinical evaluation is essential."
        ),
        "limitations": (
            "Confirms that visible redness alone CANNOT diagnose a specific underlying disease."
        ),
        "supported_claims": [
            "Facial redness can arise from diverse environmental, inflammatory, and vascular factors",
            "Visible redness is an etiologically non-specific observation",
            "Persistent or unexplained redness requires in-person medical evaluation",
        ],
        "unsupported_claims": [
            "Visible redness in an image can prove rosacea, dermatitis, or allergy",
        ],
    },
    "SRC-13": {
        "id": "SRC-13",
        "file_name": "13_Enlarged Pores.docx",
        "title": "Enlarged pores",
        "authors": "Lydia Chan, Amanda Oakley",
        "year": "2017",
        "source_type": "Official dermatology educational resource",
        "authority": "DermNet NZ",
        "identifier": "DermNet NZ Reference",
        "url": "https://dermnetnz.org/topics/enlarged-pores",
        "topic": "Facial pore anatomy, infundibular openings, and contributing factors",
        "key_findings": (
            "Facial pores are the surface depressions containing openings to sweat and sebaceous ducts. "
            "Contributing factors include higher sebum secretion, hair follicle size, loss of "
            "dermal elasticity with age, and cumulative sun damage."
        ),
        "limitations": (
            "Pores are normal structural anatomy; apparent size on camera varies with resolution, "
            "lighting angle, and viewing distance."
        ),
        "supported_claims": [
            "Pores are normal openings that carry natural oils and sweat to the surface",
            "Pore visibility is influenced by oiliness, skin elasticity, genetics, and age",
            "Pores cannot physically 'open and close' with temperature",
        ],
        "unsupported_claims": [
            "Visible pores are a medical condition or disease",
        ],
    },
    "SRC-14": {
        "id": "SRC-14",
        "file_name": "14_Wrinkles  Fine Lines.docx",
        "title": "Facial lines and wrinkles",
        "authors": "Amanda Oakley",
        "year": "2004",
        "source_type": "Official dermatology educational resource",
        "authority": "DermNet NZ",
        "identifier": "DermNet NZ Reference",
        "url": "https://dermnetnz.org/topics/facial-lines-and-wrinkles",
        "topic": "Facial rhytides, intrinsic aging, photoaging, and mechanical movement",
        "key_findings": (
            "Facial lines and wrinkles form due to intrinsic biological aging, ultraviolet damage, "
            "repeated muscle contractions (dynamic lines), gravity, and loss of structural support. "
            "Grading scales (e.g. Glogau, Fitzpatrick) assess line severity clinically."
        ),
        "limitations": (
            "Photographic analysis shows 2D shadow contours; cannot measure 3D dermal depth in millimeters."
        ),
        "supported_claims": [
            "Wrinkles result from natural aging, sun damage, and repeated facial expressions",
            "Loss of structural skin firmness makes creases more visible over time",
        ],
        "unsupported_claims": [
            "A smartphone photo can measure exact 3D microscopic wrinkle depth",
        ],
    },
    "SRC-15": {
        "id": "SRC-15",
        "file_name": "15_Blackheads & Whiteheads (Comedones).docx",
        "title": "Comedo",
        "authors": "DermNet NZ",
        "year": "2017",
        "source_type": "Official dermatology educational resource",
        "authority": "DermNet NZ",
        "identifier": "DermNet NZ Reference",
        "url": "https://dermnetnz.org/topics/comedone",
        "topic": "Follicular plugs, open and closed comedone pathology",
        "key_findings": (
            "A comedo is a plugged follicular orifice. Open comedones (blackheads) have dilated "
            "follicular openings containing oxidized keratinous material and melanin. Closed "
            "comedones (whiteheads) are uninflamed skin-colored or pale papules with narrow openings."
        ),
        "limitations": (
            "Morphology reference; cannot determine microbiological colonization from surface photos."
        ),
        "supported_claims": [
            "A comedo is an accumulation of oil and shed cells inside a hair follicle orifice",
            "Open comedones darken due to oxygen exposure at the surface opening",
            "Closed comedones remain pale or skin-toned because the opening is narrow",
        ],
        "unsupported_claims": [
            "Every tiny follicular dot visible on camera represents comedonal acne",
        ],
    },
    "SRC-16": {
        "id": "SRC-16",
        "file_name": "16_Skin Aging Biology.docx",
        "title": "Molecular mechanisms of skin aging: state of the art",
        "authors": "E Makrantonaki, C C Zouboulis",
        "year": "2007",
        "source_type": "Peer-reviewed molecular review",
        "authority": "Annals of the New York Academy of Sciences",
        "identifier": "DOI: 10.1196/annals.1404.027; PMID: 18056953",
        "url": "https://pubmed.ncbi.nlm.nih.gov/18056953/",
        "topic": "Cellular senescence, oxidative stress, and dermal extracellular matrix aging",
        "key_findings": (
            "Skin aging is driven by synergistic intrinsic factors (cellular senescence, telomere "
            "shortening, declining hormone levels) and extrinsic factors (reactive oxygen species from "
            "UV radiation), leading to degraded extracellular matrix and reduced dermal synthesis."
        ),
        "limitations": (
            "Molecular review; biological cellular senescence cannot be measured from consumer images."
        ),
        "supported_claims": [
            "Skin aging involves gradual reduction in structural proteins and cellular renewal",
            "Oxidative stress and UV exposure accelerate visible surface skin changes",
        ],
        "unsupported_claims": [
            "2D images can determine internal cellular biological age or telomere length",
        ],
    },
    "SRC-17": {
        "id": "SRC-17",
        "file_name": "17_Collagen, Elastin & Extracellular Matrix.docx",
        "title": "Molecular Mechanisms of Dermal Aging and Antiaging Approaches",
        "authors": "Jung-Won Shin, Soon-Hyo Kwon, Ji-Young Choi, Jung-Im Na, Chang-Hun Huh, Hye-Ryung Choi, Kyung-Chan Park",
        "year": "2019",
        "source_type": "Peer-reviewed molecular review",
        "authority": "International Journal of Molecular Sciences / MDPI",
        "identifier": "PMID: 31036793; PMCID: PMC6540032",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6540032/",
        "topic": "Dermal extracellular matrix, collagen degradation, MMPs, and elastin fragmentation",
        "key_findings": (
            "Dermal aging is characterized by quantitative and structural loss of type I and III "
            "collagen fibers. Matrix Metalloproteinases (MMP-1, MMP-3, MMP-9) are upregulated by "
            "reactive oxygen species and UV light, cleaving dermal collagen and fragmenting elastic fibers."
        ),
        "limitations": (
            "Biochemical and histologic review; image models cannot evaluate dermal collagen density directly."
        ),
        "supported_claims": [
            "Collagen and elastin fibers provide the structural scaffold that keeps skin firm",
            "Enzymatic breakdown of collagen (MMPs) and solar damage contribute to visible lines",
        ],
        "unsupported_claims": [
            "Visual image contours can quantify molecular collagen synthesis rates",
        ],
    },
    "SRC-21": {
        "id": "SRC-21",
        "file_name": "21_When to Seek Dermatological Consultation  Safety.docx",
        "title": "Find skin cancer: How to perform a skin self-exam and referral thresholds",
        "authors": "American Academy of Dermatology (AAD)",
        "year": "2023",
        "source_type": "Official clinical safety guidance",
        "authority": "American Academy of Dermatology (AAD)",
        "identifier": "AAD Safety Guidance",
        "url": "https://www.aad.org/public/diseases/skin-cancer/how-to-spot-skin-cancer",
        "topic": "Clinical red flags, lesion self-examination, and ABCDE screening criteria",
        "key_findings": (
            "Regular self-checks help identify skin changes early. Dermatologists advise "
            "monitoring for the ABCDE criteria (Asymmetry, Border irregularity, Color variation, "
            "Diameter >6mm, Evolving). Any lesion that bleeds, itches, fails to heal, or changes requires evaluation."
        ),
        "limitations": (
            "Educational screening tool; consumer AI must never replace in-person dermatological inspection."
        ),
        "supported_claims": [
            "Changing, irregular, bleeding, or non-healing lesions require professional evaluation",
            "Consumer AI tools are informational only and cannot screen for or rule out skin neoplasms",
        ],
        "unsupported_claims": [
            "A wellness camera assessment can clear a suspicious lesion as safe",
        ],
    },
    "SRC-22": {
        "id": "SRC-22",
        "file_name": "22_AI Dermatology Dataset Transparency & Bias.docx",
        "title": "Lack of Transparency and Potential Bias in Artificial Intelligence Data Sets and Algorithms: A Scoping Review",
        "authors": "Roxana Daneshjou, Mary P Smith, Mary D Sun, Veronica Rotemberg, James Zou",
        "year": "2022",
        "source_type": "Peer-reviewed scoping review",
        "authority": "JAMA Dermatology / AMA",
        "identifier": "PMID: 34550305; PMCID: PMC9379852",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9379852/",
        "topic": "Dermatology AI dataset transparency, benchmark reporting, and demographic bias",
        "key_findings": (
            "A review of 70 dermatology AI studies revealed critical transparency deficits: only "
            "24% of training images were publicly accessible, only 20% reported patient ethnicity, "
            "and only 10% characterized skin tone. Models trained on narrow cohorts cannot be assumed "
            "to generalize equally across diverse populations."
        ),
        "limitations": (
            "Scoping review of academic literature; establishes that AI outputs must communicate "
            "confidence carefully and avoid claiming universal clinical validation."
        ),
        "supported_claims": [
            "AI predictions reflect training datasets and may exhibit variable performance across skin tones",
            "Transparent communication of model limits and dataset boundaries is ethically essential",
        ],
        "unsupported_claims": [
            "The model possesses clinical validation across all demographic groups",
        ],
    },
    "SRC-23": {
        "id": "SRC-23",
        "file_name": "23_XAI in Dermatology Systematic Review.docx",
        "title": "Explainable artificial intelligence in skin cancer recognition: A systematic review",
        "authors": "Katja Hauser et al.",
        "year": "2022",
        "source_type": "Peer-reviewed systematic review",
        "authority": "European Journal of Cancer / Elsevier",
        "identifier": "DOI: 10.1016/j.ejca.2022.02.025; PMID: 35390650",
        "url": "https://pubmed.ncbi.nlm.nih.gov/35390650/",
        "topic": "Explainable AI (XAI), saliency maps, and Grad-CAM in dermatology",
        "key_findings": (
            "Visual attribution techniques (such as Grad-CAM and saliency maps) show which image pixels "
            "most heavily influenced a neural network's activation. However, heatmaps are model "
            "explanation aids; they do NOT prove clinical correctness, biological causality, or medical ground truth."
        ),
        "limitations": (
            "Systematic review of 37 dermatology XAI studies. Demonstrates that visual attribution "
            "must never be presented to patients as proof of medical pathology."
        ),
        "supported_claims": [
            "Grad-CAM visualizes which parts of an image influenced the model's pattern prediction",
            "Heatmaps are an explanation aid for understanding computer vision focus",
        ],
        "unsupported_claims": [
            "A heatmap proves that a biological disease is present in that tissue",
            "A heatmap shows the medical cause of a skin appearance",
        ],
    },
    "SRC-24": {
        "id": "SRC-24",
        "file_name": "24_Ethical & Safety Considerations in Dermatology AI.docx",
        "title": "Ethical considerations for artificial intelligence in dermatology: a scoping review",
        "authors": "Emily R Gordon et al.",
        "year": "2024",
        "source_type": "Peer-reviewed scoping review",
        "authority": "British Journal of Dermatology / Oxford University Press",
        "identifier": "DOI: 10.1093/bjd/ljae040; PMID: 38330217",
        "url": "https://pubmed.ncbi.nlm.nih.gov/38330217/",
        "topic": "AI ethics, non-diagnostic boundaries, safety, and clinical oversight",
        "key_findings": (
            "Dermatology AI applications require strict ethical safeguards: transparent explanation "
            "of capabilities, avoidance of misleading diagnostic claims, clear privacy protections, "
            "and preservation of the physician-patient relationship."
        ),
        "limitations": (
            "Scoping review; confirms that AI systems must frame outputs as informational pattern observations."
        ),
        "supported_claims": [
            "AI skin analysis tools must remain non-diagnostic and support human clinical judgment",
            "Systems must avoid misleading confidence claims that create false reassurance",
        ],
        "unsupported_claims": [
            "AI can independently replace dermatological clinical consultation",
        ],
    },
    "SRC-26A": {
        "id": "SRC-26A",
        "file_name": "26_Objective Skin Type Classification.docx",
        "title": "An objective skin-type classification based on non-invasive biophysical parameters",
        "authors": "J I Seo, H I Ham, J H Baek, M K Shin",
        "year": "2021",
        "source_type": "Primary clinical research",
        "authority": "Journal of the European Academy of Dermatology and Venereology (JEADV) / Wiley",
        "identifier": "DOI: 10.1111/jdv.17793; PMID: 34747517",
        "url": "https://pubmed.ncbi.nlm.nih.gov/34747517/",
        "topic": "Multi-dimensional objective biophysical skin type classification",
        "key_findings": (
            "Objective skin type classification requires measuring 5 distinct physical parameters: "
            "oiliness (Sebumeter), hydration (Corneometer), transepidermal water loss (Tewameter), "
            "elasticity (Cutometer), and erythema/pigmentation (Mexameter). Subjective surveys are unreliable."
        ),
        "limitations": (
            "Evaluated Korean adults; demonstrates conclusively that 2D camera images lack the "
            "physical sensor capabilities needed to classify objective skin type."
        ),
        "supported_claims": [
            "Skin type is an objective multi-parameter biophysical measurement",
            "Valid skin typing requires specialized physical probes, not consumer camera images",
        ],
        "unsupported_claims": [
            "A facial photo alone is sufficient to classify skin type objectively",
        ],
    },
    "SRC-26B": {
        "id": "SRC-26B",
        "file_name": "26_Sun  UV Protection.docx",
        "title": "Practice Safe Sun: Sun protection guidelines",
        "authors": "American Academy of Dermatology (AAD)",
        "year": "2024",
        "source_type": "Official clinical guidance",
        "authority": "American Academy of Dermatology (AAD)",
        "identifier": "AAD Sun Safety Guidance",
        "url": "https://www.aad.org/public/everyday-care/sun-protection/sun-safety/practice-safe-sun",
        "topic": "Ultraviolet radiation, photoaging, and photoprotection",
        "key_findings": (
            "Ultraviolet radiation (UVA and UVB) penetrates the skin, generating reactive oxygen species, "
            "damaging cellular DNA, breaking down collagen, and stimulating irregular melanin synthesis. "
            "Broad-spectrum sunscreen reduces photoaging and pigmentary alterations."
        ),
        "limitations": (
            "Public health guidance; individual lifetime UV exposure cannot be measured from a single photo."
        ),
        "supported_claims": [
            "Sun exposure is a primary external driver of both wrinkles and dark spot formation",
            "Daily photoprotection prevents further degradation of skin structural proteins",
        ],
        "unsupported_claims": [
            "Image analysis can determine an individual's cumulative lifetime UV radiation dose",
        ],
    },
    "SRC-27": {
        "id": "SRC-27",
        "file_name": "27_Facial Image-Based Skin Assessment.docx",
        "title": "Development and application of artificial intelligence-based facial skin image diagnosis system: Changes in facial skin characteristics with ageing in Korean women",
        "authors": "Hyeokgon Park et al.",
        "year": "2023",
        "source_type": "Primary AI research",
        "authority": "International Journal of Cosmetic Science / Wiley",
        "identifier": "DOI: 10.1111/ics.12924; PMID: 37881146",
        "url": "https://pubmed.ncbi.nlm.nih.gov/37881146/",
        "topic": "Deep learning analysis of facial wrinkles, pores, pigmentation, and red spots",
        "key_findings": (
            "Deep learning systems trained on clinical expert visual assessments can evaluate the area "
            "and intensity of visible facial features (wrinkles, pores, pigmentation, red spots). "
            "Pores showed notable changes in earlier adult decades, while wrinkles and pigmentation "
            "progressed prominently with age; red spots showed no straightforward correlation with age."
        ),
        "limitations": (
            "Evaluated 120 Korean women; assessed visible 2D photographic features against clinician "
            "visual scoring, NOT histological disease or biophysical skin type."
        ),
        "supported_claims": [
            "Deep learning models can detect surface visible patterns such as pores, lines, and spots",
            "Visible features change across facial zones and age groups",
        ],
        "unsupported_claims": [
            "AI photographic scoring equals histological biopsy or clinical medical diagnosis",
        ],
    },
    "SRC-28": {
        "id": "SRC-28",
        "file_name": "28_Skin Tone  Fitzpatrick Skin Phototype.docx",
        "title": "Skin typing: Fitzpatrick grading and others",
        "authors": "Vishal Gupta, Vinod Kumar Sharma",
        "year": "2019",
        "source_type": "Peer-reviewed clinical review",
        "authority": "Clinics in Dermatology / Elsevier",
        "identifier": "DOI: 10.1016/j.clindermatol.2019.07.010; PMID: 31896400",
        "url": "https://pubmed.ncbi.nlm.nih.gov/31896400/",
        "topic": "Fitzpatrick skin phototyping, erythema/tanning reactivity, and visual limits",
        "key_findings": (
            "The Fitzpatrick phototype scale measures an individual's constitutional propensity to burn "
            "versus tan upon initial unacclimated UV exposure. It is a functional physiological response "
            "scale, NOT a simple measurement of baseline skin color."
        ),
        "limitations": (
            "Clinical review; demonstrates that visual skin tone in an RGB photo cannot be equated "
            "with true Fitzpatrick UV response phototype."
        ),
        "supported_claims": [
            "Skin response to sun exposure varies by individual phototype and melanin genetics",
            "Visual skin tone alone cannot predict biological UV burn thresholds",
        ],
        "unsupported_claims": [
            "Camera RGB values can reliably categorize Fitzpatrick phototype",
        ],
    },
    "SRC-29": {
        "id": "SRC-29",
        "file_name": "29_Dermatology AI  Facial Skin Assessment Validation.docx",
        "title": "Artificial Intelligence Applications in Dermatology: Where Do We Stand?",
        "authors": "Arieh Gomolin, Elena Netchiporouk, Robert Gniadecki, Ivan V Litvinov",
        "year": "2020",
        "source_type": "Peer-reviewed review",
        "authority": "Frontiers in Medicine",
        "identifier": "PMID: 32296706; PMCID: PMC7136423",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7136423/",
        "topic": "AI in dermatology, black-box limitations, non-standardized photos, and guidance role",
        "key_findings": (
            "AI neural networks are reflection of training datasets ('black box') and cannot explain "
            "clinical biological logic like a physician. Unstandardized photography (lighting, angles) "
            "strongly influences outputs. AI is positioned as an informational guidance aid, not an "
            "absolute diagnostic tool. Improving lay descriptions is essential for safe public trust."
        ),
        "limitations": (
            "Literature review; directly validates that AI must be presented with lay explanations "
            "and explicitly separated from medical diagnostic claims."
        ),
        "supported_claims": [
            "Deep learning algorithms identify visual patterns without knowing clinical biological causes",
            "Clear lay explanations help users understand AI outputs safely",
            "AI functions as an informational guidance aid, not a diagnostic replacement",
        ],
        "unsupported_claims": [
            "AI decisions represent verified medical diagnoses",
        ],
    },
}


def get_source_by_id(source_id: str) -> Optional[EvidenceSource]:
    """Retrieve structured source metadata by its ID."""
    return EVIDENCE_SOURCES.get(source_id)


def get_sources_for_concern(source_ids: list[str]) -> list[EvidenceSource]:
    """Retrieve multiple structured sources by ID list."""
    return [EVIDENCE_SOURCES[sid] for sid in source_ids if sid in EVIDENCE_SOURCES]
