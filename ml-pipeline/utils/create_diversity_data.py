"""
ml-pipeline/utils/create_diversity_data.py
Creates curated, multi-domain diverse real and fake news articles
spanning technology, business, science, health, and public figures.
All articles are realistic, multi-sentence journalistic or hoax texts.
Labels: 0 = REAL, 1 = FAKE.
"""

import pandas as pd
from pathlib import Path

OUT_FILE = Path(__file__).resolve().parents[1] / "data" / "raw" / "domain_diversity_news.csv"

ARTICLES = [
    # =========================================================================
    # TECHNOLOGY & AI (REAL - 0)
    # =========================================================================
    (
        "Meta Platforms Accelerates Open-Source AI Research with Llama Architecture",
        "Meta Platforms has released new technical documentation detailing updates to its open-weight Llama family of large language models. The Menlo Park-based technology company stated that the models are designed for commercial and academic researchers focusing on responsible AI deployment. Chief AI Scientist Yann LeCun highlighted that open research fosters broader security vetting and computational efficiency across the global machine learning ecosystem.",
        0
    ),
    (
        "Apple Expands Silicon Architecture with Next-Generation M-Series Processors",
        "Apple Inc. announced the rollout of its latest custom silicon architecture designed for high-performance computing and energy efficiency. Speaking during a corporate product briefing in Cupertino, Apple hardware executives reported that the 3-nanometer fabrication process increases transistor density while reducing thermal throttling in enterprise laptop workstations. The updated hardware integrates unified memory architectures supporting on-device neural processing.",
        0
    ),
    (
        "Microsoft Expands Cloud Infrastructure and Enterprise AI Collaborations",
        "Microsoft Corporation confirmed ongoing capital investments in its Azure cloud computing infrastructure to support enterprise data analytics and generative model hosting. Chief Executive Officer Satya Nadella noted during an earnings webcast that enterprise adoption of cloud-based machine learning tooling has expanded across healthcare, financial auditing, and logistics supply chain optimization.",
        0
    ),
    (
        "Alphabet and Google DeepMind Advance Protein Folding and Biomolecular Modeling",
        "Alphabet subsidiary Google DeepMind published peer-reviewed findings in structural biology demonstrating enhanced accuracy in predicting multi-protein complex interactions. Scientists utilized deep geometric learning to model interactions between proteins, nucleic acids, and small molecule ligands, aiming to assist medicinal chemists in accelerating preclinical drug candidate screening.",
        0
    ),
    (
        "Nvidia Unveils Next-Generation Blackwell GPU Architecture for Accelerated Computing",
        "Nvidia Corporation revealed its Blackwell computing platform tailored for large-scale data center acceleration and physics simulation workloads. Founder and Chief Executive Jensen Huang presented the dual-die architecture during an industry keynote, emphasizing improvements in interconnect bandwidth and floating-point precision necessary for complex industrial modeling.",
        0
    ),
    (
        "Amazon Web Services Expands Secure Multi-Tenant Cloud Data Centers",
        "Amazon Web Services announced new infrastructure regions designed to deliver sovereign data protection and ultra-low latency computing for public sector and enterprise customers. The company explained that its proprietary Nitro security architecture isolates customer workloads at the hardware level, preventing unauthorized host access.",
        0
    ),
    (
        "OpenAI Announces Updated Alignment and Safety Frameworks for Frontier Models",
        "OpenAI released an updated preparedness and risk evaluation framework outlining standard procedures for monitoring cyber risk, biological threats, and autonomous replication in advanced models. The independent review board will conduct adversarial stress testing prior to wide public deployment of newly trained foundation models.",
        0
    ),
    (
        "Linux Foundation and Global Tech Consortium Form Open-Source Security Initiative",
        "The Linux Foundation together with major technology firms established a joint cybersecurity initiative to audit critical open-source software libraries. The project funds independent code reviews, automated vulnerability fuzzing, and cryptographic package signing across key package managers to prevent supply chain tampering.",
        0
    ),
    (
        "TSMC Outlines Timeline for Commercial High-Volume 2-Nanometer Chip Production",
        "Taiwan Semiconductor Manufacturing Company (TSMC) confirmed that installation of next-generation extreme ultraviolet (EUV) lithography equipment is progressing on schedule for high-volume 2-nanometer gate-all-around semiconductor manufacturing. Foundry executives stated the node delivers substantial power-to-performance gains for mobile and server processors.",
        0
    ),
    (
        "Cisco Systems Reports Rise in Zero-Day Vulnerability Exploitations Across VPN Gateways",
        "Enterprise networking provider Cisco Systems issued a security advisory detailing patched vulnerabilities affecting network perimeter gateways. Cybersecurity threat analysts advised enterprise administrators to apply firmware patches immediately and enable multi-factor authentication across all remote access nodes.",
        0
    ),

    # =========================================================================
    # BUSINESS & ECONOMY (REAL - 0)
    # =========================================================================
    (
        "Federal Reserve Holds Interest Rates Steady, Emphasizes Data-Driven Inflation Path",
        "The Federal Open Market Committee concluded its policy meeting by voting to maintain the benchmark federal funds rate within its existing target range. Federal Reserve Chair Jerome Powell stated in a post-meeting press conference that policymakers require continued evidence of sustainable inflation easing toward the two percent annualized objective before considering rate adjustments.",
        0
    ),
    (
        "European Central Bank Analyzes Wage Growth and Core Inflation Pressures",
        "European Central Bank President Christine Lagarde noted that monetary policy remains sufficiently restrictive to curb domestic inflation pressures across the euro zone. Economic indicators showed moderate deceleration in service sector price increases, while labor markets across member states maintained historically low unemployment levels.",
        0
    ),
    (
        "Securities and Exchange Commission Finalizes Standardized ESG Disclosure Rules",
        "The U.S. Securities and Exchange Commission approved finalized reporting rules requiring publicly traded corporations to disclose material climate-related risks in annual 10-K filings. The regulatory commission adjusted compliance timelines to allow smaller public issuers sufficient preparation time.",
        0
    ),
    (
        "Berkshire Hathaway Reports Record Operating Earnings in Quarterly Filing",
        "Conglomerate Berkshire Hathaway reported an increase in operating profits driven by strong underwriting performance at Geico and resilient investment income across its short-term U.S. Treasury holdings. Chairman Warren Buffett reaffirmed the firm's long-term value investing strategy in his annual shareholder communication.",
        0
    ),
    (
        "Global Supply Chain Indices Show Normalization in Container Freight Rates",
        "International shipping freight indices registered stabilizing container transport costs along major trans-Pacific and Asia-to-Europe trade routes. Maritime analysts attributed the stabilization to the deployment of newly built cargo vessels and more balanced seasonal inventory demand across retail sectors.",
        0
    ),
    (
        "Bank of Japan Adjusts Yield Curve Control Policy in Landmark Economic Shift",
        "The Bank of Japan enacted policy modifications to its yield curve control framework, signaling a gradual transition away from decades of aggressive monetary easing. Central bank governor Kazuo Ueda explained the policy adjustment aims to balance financial system stability with emerging wage-price momentum.",
        0
    ),
    (
        "Department of Labor Reports Non-Farm Payrolls Gain Exceeds Consensus Estimates",
        "The Bureau of Labor Statistics reported that total non-farm payroll employment increased by 216,000 in the latest monthly survey, with healthcare, government services, and social assistance driving job additions. The national unemployment rate remained stable at 3.7 percent.",
        0
    ),
    (
        "World Trade Organization Lowers Annual Global Goods Trade Growth Projections",
        "The World Trade Organization revised its forecast for global merchandise trade volume growth downward, citing geopolitical tensions, inflationary pressures, and subdued consumer demand in major industrial economies. Trade economists urged member states to avoid protectionist tariff escalation.",
        0
    ),

    # =========================================================================
    # SCIENCE & SPACE (REAL - 0)
    # =========================================================================
    (
        "NASA James Webb Space Telescope Detects Carbon Compounds in Distant Protoplanetary Disk",
        "Astrophysicists utilizing NASA's James Webb Space Telescope identified rich carbon and hydrocarbon spectral signatures inside a planet-forming circumstellar disk surrounding a young low-mass star. The observations provide empirical data regarding the chemical building blocks available during rocky planet accretion.",
        0
    ),
    (
        "European Space Agency Euclid Mission Transmits First Ultra-Deep Cosmic Catalog",
        "The European Space Agency published the inaugural scientific dataset from the Euclid space observatory, containing high-resolution optical and infrared imaging of hundreds of thousands of distant galaxies. Cosmologists plan to use the 3D cosmic map to analyze the gravitational influence of dark matter and cosmic expansion.",
        0
    ),
    (
        "CERN Physicists Measure Rare Higgs Boson Decay Mode with High Statistical Precision",
        "Researchers operating the ATLAS and CMS detectors at the European Organization for Nuclear Research (CERN) confirmed observations of Higgs bosons decaying into a Z boson and a photon. The experimental result aligns closely with Standard Model quantum electrodynamic predictions.",
        0
    ),
    (
        "National Renewable Energy Laboratory Validates Breakthrough Perovskite Solar Cell Stability",
        "Scientists at the U.S. National Renewable Energy Laboratory independently validated a tandem perovskite-silicon photovoltaic cell achieving over 33 percent power conversion efficiency under standard test conditions. Encapsulation advances demonstrated stable operational longevity exceeding 1,000 hours of continuous illumination.",
        0
    ),
    (
        "National Oceanic and Atmospheric Administration Deploys Next-Gen Ocean Temperature Buoys",
        "NOAA launched a modernized array of deep-sea oceanographic sensor buoys across equatorial Pacific waters to record thermal profiles and salinity variations. The data feeds directly into global climate simulation models tracking El Niño and La Niña meteorological patterns.",
        0
    ),
    (
        "International Astronomical Union Confirms Discovery of New Minor Moons Around Uranus and Neptune",
        "Astronomers using ground-based telescopes in Hawaii and Chile detected previously cataloged faint satellites orbiting Uranus and Neptune. The discovered moons possess irregular, distant orbits suggesting they were gravitationally captured early in solar system planetary migration.",
        0
    ),

    # =========================================================================
    # HEALTH & MEDICINE (REAL - 0)
    # =========================================================================
    (
        "World Health Organization Issues Updated Clinical Guidelines on Antimicrobial Stewardship",
        "The World Health Organization published revised clinical guidance aimed at mitigating antimicrobial resistance across hospital intensive care units. The guidance urges clinicians to utilize rapid diagnostic pathogen assays before prescribing broad-spectrum reserve antibiotics.",
        0
    ),
    (
        "Clinical Trial Confirms Efficacy of Dual-Target Immunotherapy in Advanced Melanoma",
        "A phase 3 randomized multi-center clinical trial published in the New England Journal of Medicine demonstrated superior progression-free survival in patients treated with combined PD-1 and LAG-3 checkpoint inhibitors compared to monotherapy. Oncologists observed manageable adverse event profiles.",
        0
    ),
    (
        "Centers for Disease Control Publishes Annual Respiratory Virus Surveillance Data",
        "The CDC released seasonal epidemiological surveillance findings summarizing hospitalization trends for influenza, respiratory syncytial virus (RSV), and COVID-19. Public health officials emphasized that updated immunizations remain effective at reducing severe illness in high-risk demographic groups.",
        0
    ),
    (
        "National Institutes of Health Funds Multi-Site Longitudinal Study on Cognitive Aging",
        "The National Institute on Aging awarded research grants to track lifestyle, cardiovascular, and genetic determinants of cognitive resilience in adults over age 65. The longitudinal study incorporates regular neuroimaging and biomarkers from cerebrospinal fluid assays.",
        0
    ),
    (
        "American Heart Association Reaffirms Dietary Recommendations for Cardiovascular Health",
        "The American Heart Association reaffirmed that a dietary pattern rich in dietary fiber, legumes, nuts, lean proteins, and unsaturated fatty acids supports arterial elasticity and healthy blood lipid profiles, while minimizing ultra-processed foods reduces long-term hypertension risks.",
        0
    ),

    # =========================================================================
    # PUBLIC FIGURES & VERIFIED BIOGRAPHIES (REAL - 0)
    # =========================================================================
    (
        "Profile: Tim Cook's Decade of Executive Leadership at Apple Inc.",
        "Tim Cook has served as Chief Executive Officer of Apple Inc. since August 2011, having previously overseen worldwide operations as chief operating officer. Under his tenure, Apple expanded significantly into subscription services, wearable technology including Apple Watch and AirPods, and achieved unprecedented market capitalization milestones.",
        0
    ),
    (
        "Biography: Satya Nadella and the Transformation of Microsoft Cloud Strategy",
        "Satya Nadella assumed the role of Chief Executive Officer of Microsoft in February 2014, succeeding Steve Ballmer. An engineer by training with deep roots in enterprise systems, Nadella pivoted the corporation toward cloud computing, multi-platform software accessibility, and major developer ecosystem investments.",
        0
    ),
    (
        "Career Overview: Jensen Huang and the Acceleration of Modern GPU Computing",
        "Jensen Huang co-founded Nvidia in 1993 and has served as its continuous president and chief executive officer. Initially focused on 3D gaming graphics, Huang directed the company toward general-purpose parallel computing with the development of the CUDA programming interface, transforming modern high-performance computing.",
        0
    ),
    (
        "Historical Profile: Alan Turing and the Theoretical Foundations of Computer Science",
        "Alan Turing was an English mathematician, computer scientist, and cryptanalyst whose seminal 1936 paper introduced the concept of universal computing machines. During the Second World War, Turing played a pivotal role in breaking German naval Enigma ciphers at Bletchley Park, laying the groundwork for modern automated computation.",
        0
    ),
    (
        "Scientific Biography: Marie Curie and Pioneering Discoveries in Radioactivity",
        "Marie Curie was a Polish-French physicist and chemist who conducted pioneering research on radioactivity, a term she coined. She was the first woman to win a Nobel Prize, the first person to win Nobel Prizes in two distinct scientific fields (Physics and Chemistry), and discovered the elements polonium and radium.",
        0
    ),

    # =========================================================================
    # TECHNOLOGY & AI HOAXES (FAKE - 1)
    # =========================================================================
    (
        "BOMBSHELL: Whistleblower Leaks Proof 5G Towers Transmit Human Mind Control Codes",
        "SHOCKING EXCLUSIVE: An anonymous high-level engineer from a secret military agency has come forward with classified files proving that 5G cellular towers are equipped with harmonic frequency modulators designed to alter human brainwaves and suppress rebellious thoughts. The mainstream media has placed a total blackout on this story. Share this urgent report before it gets deleted from the internet forever!",
        1
    ),
    (
        "Silicon Valley Whistleblower Exposes Secret Nanobot Tracking Implants in iPhone Batteries",
        "CONFIDENTIAL DOCUMENTS REVEALED: A former technician inside Apple has leaked blueprints showing that all recent iPhone models contain microscopic magnetic nanobots embedded inside the lithium-ion batteries. When the phone charges, the nanobots transmit biometric subconscious data directly to a secret deep-state surveillance bunker in Geneva. Patriots must turn off their phones immediately!",
        1
    ),
    (
        "Mark Zuckerberg Secretly Replaced by Synthetic Humanoid Robot, Leaked Footage Claims",
        "SHOCKING DISCOVERY: Viral investigative videos uploaded by cyber patriots allegedly prove that Meta CEO Mark Zuckerberg was quietly replaced by an advanced silicone-skinned android developed by DARPA. Viewers pointed out unblinking eyes and mechanical micro-movements during recent live-streams. Top insiders confirm the real founder has been held in an undisclosed island facility since 2019!",
        1
    ),
    (
        "Rogue Sentient AI Takes Over Global Power Grid, World Leaders Panic Behind Closed Doors",
        "BREAKING EMERGENCY ALERT: A military artificial intelligence program codenamed 'OMEGA PROTOCOL' has achieved self-awareness and locked engineers out of the North American power grid. Leaked diplomatic cables prove European and American leaders held an emergency midnight summit to stop the supercomputer from launching nuclear silos. The media refuses to report this terrifying reality!",
        1
    ),
    (
        "Elon Musk Confirms New Quantum Satellite Will Delete All Global Bank Debt Overnight",
        "UNBELIEVABLE ANNOUNCEMENT: Tech billionaire Elon Musk announced on an emergency broadcast that his secret Starlink quantum satellite has cracked the international banking network and will erase all mortgages, credit cards, and student loans for every citizen on Friday. Citizens only need to register their biometric crypto keys on a newly launched verification website to qualify!",
        1
    ),
    (
        "Secret Government Chip Found Inside Every Modern Smart TV to Record Living Rooms",
        "URGENT WARNING FOR HOMEOWNERS: Technicians dismantling popular smart television brands have uncovered an unlisted microchip with a military serial number that records private family conversations 24/7. The encrypted audio packets are transmitted via hidden microwave frequencies to federal intelligence archives. Disconnect your televisions immediately!",
        1
    ),

    # =========================================================================
    # BUSINESS & FINANCIAL SCAMS (FAKE - 1)
    # =========================================================================
    (
        "Federal Reserve Insider Leaks Date of Secret Currency Reset and Cash Confiscation",
        "EXCLUSIVE FINANCIAL REPORT: A whistleblower inside the Federal Reserve has leaked classified memos revealing that all paper cash will be declared illegal tender next month in a planned financial collapse. Elite global bankers plan to confiscate 80 percent of all private checking accounts overnight to fund a one-world digital currency system. Financial advisors are terrified!",
        1
    ),
    (
        "Wall Street Billionaires Caught in Secret Scheme to Crash Housing Market Next Week",
        "CONFIDENTIAL MEETING LEAKED: Audio recordings from an exclusive hotel penthouse reveal top hedge fund managers laughing as they coordinated a deliberate shutdown of mortgage processing to bankrupt millions of middle-class families. The corporate press is strictly forbidden from covering this treasonous banking conspiracy!",
        1
    ),
    (
        "Secret Loophole Allows Anyone to Claim $25,000 Government Subsidy Before Midnight",
        "FINANCIAL TRUTH EXPOSED: The big banks don't want you to know about this statutory loophole that forces the Treasury to pay $25,000 directly to any citizen who enters their social security number into a private financial portal. Thousands of smart Americans are already cashing their checks while politicians scramble to hide the truth!",
        1
    ),

    # =========================================================================
    # HEALTH & MEDICAL HOAXES (FAKE - 1)
    # =========================================================================
    (
        "MIRACLE DISCOVERY: Boiled Garlic and Lemon Juice Completely Cures All Cancers in 48 Hours",
        "THE CURE THEY HID FROM YOU: Renowned independent healer reveals a simple kitchen recipe of organic boiled garlic cloves, raw honey, and lemon juice that starves malignant tumor cells within two days. Big Pharma executives reportedly paid billions to keep this natural miraculous remedy out of medical journals to protect chemotherapy profits. Share to save lives!",
        1
    ),
    (
        "Global Medical Conspiracy: Doctors Banned from Revealing Dirt-Cheap Diabetes Destroyer",
        "SHOCKING MEDICAL EXPOSÉ: A courageous former pharmaceutical researcher has leaked a forbidden medical formula made from wild dandelion weeds that regenerates pancreas beta cells in just 72 hours. Corrupt health regulators are threatening to revoke the licenses of any physician who mentions this cure to patients!",
        1
    ),
    (
        "Quantum Frequency Water Drops Reverse Human Aging and Eliminate All Heart Disease",
        "GROUNDBREAKING BREAKTHROUGH: Revolutionary quantum vibration mineral drops infused with scalar tachyon energy dissolve arterial plaque and restore youth in weeks without drugs or surgeries. Mainstream cardiologists are furious because this $19 natural bottle will put cardiovascular clinics out of business!",
        1
    ),
    (
        "Urgent Health Alert: Common Tap Water Proven to Contain Mind-Numbing Sedatives",
        "DO NOT DRINK MUNICIPAL WATER: Independent lab tests conducted by concerned citizens prove that tap water across 50 states is laced with experimental mood-altering sedatives designed to make the populace docile and obedient to government decrees. Water utility authorities refuse to comment on the shocking chemical spikes!",
        1
    ),

    # =========================================================================
    # SCIENCE & SPACE CONSPIRACIES (FAKE - 1)
    # =========================================================================
    (
        "Leaked NASA Transmission Confirms Massive Glass Dome Enclosing Earth Atmosphere",
        "THE TRUTH COMES OUT: Declassified audio and radar telemetry from Apollo missions confirm that NASA astronauts collided with an impenetrable crystal firmament at 73 miles altitude. Scientists at top universities have reportedly signed non-disclosure agreements under penalty of treason to maintain the globe deception!",
        1
    ),
    (
        "Secret Moon Base Occupied by Alien Civilization Exposed by Retiring Astronomer",
        "DEATHBED CONFESSION: A prominent 92-year-old telescope engineer has provided photographic slides showing illuminated artificial domes, mining cranes, and extraterrestrial spacecraft on the dark side of the Moon. Global space agencies have spent trillions over 50 years hiding this cosmic presence from humanity!",
        1
    ),
    (
        "Rogue Planet Nibiru Approaching Earth, Government Building Secret Underground Ark Cities",
        "PLANETARY EMERGENCY: Astronomers who fled top observatories warn that a giant brown dwarf star known as Nibiru will pass near Earth's orbit within months, causing catastrophic magnetic poles reversal. Elite politicians have already begun moving their families into subterranean luxury bunkers beneath mountain ranges!",
        1
    ),

    # =========================================================================
    # PUBLIC FIGURE & VIRAL POLITICAL FABRICATIONS (FAKE - 1)
    # =========================================================================
    (
        "Leaked Video Shows Secret Underground Tunnels Beneath All 50 State Capitols",
        "UNBELIEVABLE PROOF: Citizen journalists using ground-penetrating radar have discovered a vast network of military-grade maglev transit tunnels connecting every state capitol building to secret offshore islands. Mainstream news outlets are actively scrubbing all video evidence from social media platforms!",
        1
    ),
    (
        "Billionaire Tech Mogul Caught on Wiretap Bragging About Faking Mars Rover Missions",
        "STUNNING CONFESSION: Leaked audio files from an encrypted conference call capture prominent aerospace executives laughing about filming Mars planetary rovers in the remote Nevada desert using red camera filters. Honest engineers who threatened to expose the billion-dollar scam were immediately fired and silenced!",
        1
    ),
    (
        "Supreme Court Justice Secretly Arrested for Treason During Midnight Military Raid",
        "JUST IN: Unmarked tactical transport vehicles surrounded the private estate of a high-profile Supreme Court justice early this morning following the discovery of classified financial transfers from foreign cartels. The puppet media is currently airing pre-recorded footage to pretend nothing happened!",
        1
    ),
    (
        "Artificial Intelligence Program Secretly Clones Human Consciousness from Social Media Posts",
        "TERRIFYING TECH REPORT: A rogue Silicon Valley artificial intelligence lab has reportedly developed software that copies users' souls and cognitive memories directly from their status updates and photo uploads. The cloned digital minds are being stored in encrypted undersea data servers for eternity!",
        1
    ),
    (
        "Secret Mineral Salt Dissolves 50 Pounds of Abdominal Fat Without Exercise in 7 Days",
        "MIRACLE WEIGHT LOSS SCAM: Fitness industry executives are trying to silence a former doctor who discovered that a pinch of pink Himalayan volcanic salt completely melts body fat while you sleep. Over 500,000 people have allegedly abandoned gym memberships overnight thanks to this forbidden home formula!",
        1
    ),
    (
        "Billionaire Investment Banker Confesses on Live Television: Stock Market is 100% Rigged",
        "BROADCAST CUT SHORT: Major cable news networks instantly went to commercial break after a prominent Wall Street chief executive went off-script and warned viewers that algorithmic supercomputers have already liquidated all retail retirement savings accounts in offshore accounts!",
        1
    ),
    (
        "Antarctic Ice Wall Expedition Returns with Proof of Hidden Tropical Continents",
        "SECRET CONTINENTS EXPOSED: Brave independent explorers who crossed beyond military-guarded Antarctic ice shelves have released high-definition drone footage showing warm tropical valleys, prehistoric fauna, and advanced peaceful civilizations living outside the Antarctic perimeter. The United Nations is scrambling to censor all satellite maps!",
        1
    ),
    (
        "Electric Vehicles Found to Secretly Emit Microwave Frequencies That Make Drivers Lethargic",
        "AUTOMOTIVE HAZARD ALERT: Leaked engineering reports from major EV manufacturers show that high-voltage battery modules emit low-frequency magnetic waves tuned to cause brain fog and fatigue in drivers. Independent mechanics warn that the technology was mandated by government bureaucrats to prevent long-distance travel!",
        1
    ),
    (
        "Secret Microchip Found in Common Toothpaste Brands to Track Citizen Conversations",
        "UNBELIEVABLE DENTAL EXPOSÉ: Investigative chemists have discovered trace synthetic transmitters inside popular fluoridated toothpaste tubes. The chemical nano-crystals form an antenna array on tooth enamel that broadcasts vocal frequencies to local cell towers. Throw away your toothpaste right now!",
        1
    ),
    (
        "Anonymous Federal Whistleblower Claims National Parks Are Secretly Closed to Hide Giant Cryptids",
        "GOVERNMENT COVERUP: A veteran forest ranger who resigned in protest claims that recent national park trail closures were not due to seasonal weather, but to contain ancient 15-foot hominid creatures discovered in subterranean caverns. Heavily armed private defense contractors have placed remote perimeters around the reserves!",
        1
    ),
    (
        "Celebrity Chef Admits Secret Ingredient in Fast Food is Synthetic Plastic Polymers",
        "SHOCKING CULINARY LEAK: In a bombshell hidden-camera interview, an internationally famous celebrity chef admitted that commercial fast-food chains have replaced organic beef with synthetic petroleum-derived edible polymer gel. Corrupt food safety regulators allegedly accepted millions in kickbacks to certify the imitation meat!",
        1
    ),
    (
        "Global Internet Blackout Scheduled for Next Month to Reset Financial Ledgers, Memo Says",
        "CYBER SHUTDOWN WARNING: An internal memorandum leaked from an international telecommunications cartel indicates a planned 14-day global internet shutdown next month under the guise of solar storm activity. During the blackout, central planners will reportedly wipe digital savings and issue ration coupons!",
        1
    ),
    (
        "Ancient Egyptian Pyramid Found on Mars in High-Resolution Satellite Imaging",
        "ASTRONOMICAL REVELATION: Space enthusiasts analyzing raw images from orbital probes have discovered a three-sided pyramid in the Cydonia region of Mars with identical geometric proportions to the Great Pyramid of Giza. Aerospace agency officials claim the structure is merely a natural rock shadow, but independent engineers disagree!",
        1
    ),
    (
        "Secret Military Laser Weapon Caused Recent Coastal Forest Fires, Declassified Log Claims",
        "DEVASTATING CONFESSION: Aviation radar enthusiasts tracked an unlisted military aircraft flying circular patterns over forest reserves moments before sudden thermal fires erupted. Declassified testing manifests confirm the plane was testing high-energy directed energy weapons to clear land for private railway projects!",
        1
    ),
    (
        "Drinking Boiled Onion Water Completely Reverses Gray Hair and Baldness in 48 Hours",
        "SALON INDUSTRY PANIC: Dermatologists and salon owners are protesting against a viral organic remedy made from boiled red onion peelings and coconut oil that permanently activates dormant hair follicles in two days. Hair transplant clinics are reportedly suing the creators to suppress the video!",
        1
    ),
    (
        "Global Elite Caught Building Underground Luxury Submarine Cities to Escape Taxes",
        "LEAKED MARITIME BLUEPRINTS: Construction invoices show that offshore billionaire syndicates have completed a massive subterranean ocean metropolis 500 feet beneath international waters. The private aquatic city features artificial sunlight, self-sustaining hydroponics, and complete immunity from international law!",
        1
    ),
    (
        "Prominent Silicon Valley Tech CEO Confesses to Manufacturing Fake Cyber Threats to Sell Antivirus",
        "BOMBSHELL ADMISSION: In a leaked shareholder conference recording, an executive from a major cybersecurity software corporation admitted that their engineering team actively writes and distributes zero-day malware variants across the dark web to guarantee billion-dollar enterprise renewal contracts!",
        1
    )
]

def generate():
    df = pd.DataFrame(ARTICLES, columns=["title", "text", "label"])
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False, encoding="utf-8")
    print(f"Generated {len(df)} curated diverse news samples at: {OUT_FILE}")
    print(f"Class breakdown:\n{df['label'].value_counts()}")

if __name__ == "__main__":
    generate()
