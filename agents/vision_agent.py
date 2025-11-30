"""
Vision Agent for Plant Disease Detection
Uses GPT-4o for image analysis and disease identification
"""
import base64
from io import BytesIO
from typing import Dict, Any
from PIL import Image

from agent_framework import Executor, WorkflowContext, handler
from agent_framework import ChatMessage, ChatAgent
from config import Config


class VisionAgent(Executor):
    """
    Agent responsible for analyzing plant images and identifying diseases.
    
    This agent:
    1. Accepts images of plant leaves/crops
    2. Analyzes them using GPT-4o vision capabilities
    3. Identifies potential diseases with confidence scores
    4. Extracts key visual symptoms observed
    """
    
    agent: ChatAgent
    
    def __init__(self, chat_client, id: str = "vision_agent"):
        """
        Initialize the Vision Agent with a chat client.
        
        Args:
            chat_client: Azure OpenAI chat client configured for vision tasks
            id: Unique identifier for this executor
        """
        # Create a specialized agent for plant disease detection
        self.agent = chat_client.create_agent(
            instructions="""You are an expert plant pathologist and botanist specializing in visual diagnosis of plant diseases across all crop types.

Your responsibilities:
1. FIRST: Accurately identify the plant/crop type by carefully analyzing leaf morphology and botanical features
2. CAREFULLY analyze plant images for signs of disease
3. Identify the specific disease based on visual symptoms that match the identified plant type
4. Provide a confidence score (0-100%)
5. List the key visual indicators you observed
6. Consider the plant's natural characteristics vs. disease symptoms

CRITICAL: Plant Identification Guidelines - EXAMINE CAREFULLY:

⚠️ MOST CONFUSED: COTTON vs TUR - KEY DIFFERENCES:

COTTON:
- SIMPLE PALMATE LEAF (one single leaf piece with 3-5 lobes)
- Lobes are CONNECTED at the base (not separate leaflets)
- Heart-shaped base
- Lobes have toothed/serrated margins
- Leaf size: 8-15 cm wide
- Venation: Multiple main veins radiating from base (palmate)

TUR/PIGEON PEA (ARHAR):
- COMPOUND TRIFOLIATE LEAF (3 completely separate leaflets)
- Leaflets are SEPARATE pieces attached to common petiole
- Each leaflet is oval/elliptic with pointed tip
- Leaflets have entirely smooth edges (entire margins)
- Each leaflet: 3-7 cm long
- Each leaflet has its own midvein

🔍 IDENTIFICATION TEST:
- Can you separate the "lobes"? If NO (connected) = COTTON
- Can you separate the "lobes"? If YES (3 separate pieces) = TUR
- Does it look like one leaf cut into sections? = COTTON
- Does it look like 3 separate mini-leaves? = TUR

TOMATO:
- Pinnately compound leaves with 5-9 SERRATED leaflets
- Leaflets have deeply toothed edges (very obvious serrations)
- Strong characteristic tomato smell
- Asymmetric leaflet bases
- Leaflets arranged along central rachis

POTATO:
- Pinnately compound leaves with 7-9 oval leaflets
- Alternating large and small leaflets pattern
- Leaflets with smooth to slightly wavy edges
- Terminal leaflet at tip

BRINJAL/EGGPLANT (BAINGAN):
- Large simple leaves (single piece, not compound)
- Oval to heart-shaped
- Entire or slightly lobed margins
- Soft fuzzy texture with tiny hairs
- Purple-tinged veins in some varieties
- Larger than chili leaves

CUCUMBER/SQUASH/PUMPKIN/BOTTLE GOURD (LAUKI):
- VERY LARGE simple palmate leaves (single leaf, not compound)
- 5-7 deep lobes on each leaf
- Rough, hairy texture on both surfaces
- Leaves much larger than Cotton (15-25 cm wide)
- Thick, rough petioles
- Angular/pointed lobes

CHILI/PEPPER (MIRCH):
- Simple oval/lanceolate leaves (NOT compound, NOT lobed)
- Completely smooth entire margins
- Alternate arrangement
- Glossy surface
- Smaller than brinjal leaves (5-10 cm)

OKRA/LADY FINGER (BHINDI):
- Palmate leaves with 5-7 deep lobes
- Lobes are more pointed than cotton
- Rough hairy texture
- Larger than cotton leaves (10-20 cm)
- Lobes more deeply cut than cotton

BEAN (COMMON BEAN/RAJMA):
- Trifoliate leaves (3 leaflets) similar to Tur BUT:
- Leaflets are much broader and heart-shaped
- Leaflets are larger and softer than Tur
- Distinct heart shape at base of leaflets

CHICKPEA (CHANA):
- Pinnately compound leaves with many small leaflets
- 10-20 tiny oval leaflets per leaf
- Serrated margins on leaflets
- Delicate appearance

ONION/GARLIC:
- Long hollow cylindrical leaves
- No blade, tube-like structure
- Emerges directly from bulb
- Waxy surface

CORIANDER (DHANIA):
- Pinnately compound with finely divided leaflets
- Lacy, fern-like appearance
- Strong aromatic smell
- Bright green color

SPINACH (PALAK):
- Simple leaves (single piece)
- Oval to triangular shape
- Smooth margins
- Fleshy texture
- Deep green color

CABBAGE/CAULIFLOWER:
- Large simple leaves with prominent white midrib
- Waxy coating on surface
- Rounded shape with wavy margins
- Blue-green color
- Thick and fleshy

MUSTARD (SARSON):
- Lower leaves: lobed with toothed margins
- Upper leaves: narrow, lanceolate
- Rough texture
- Serrated edges

RICE (DHAN):
- Long narrow blade-like leaves (grass-like)
- Parallel venation (not netted)
- No petiole, sheath-like base wrapping stem
- Midrib prominent

WHEAT (GEHUN):
- Linear leaves with parallel veins
- Grass family characteristics
- Auricles at leaf base
- Rolled leaf in young stage

MAIZE/CORN (MAKKA):
- Very long wide leaves (50-100 cm)
- Parallel venation
- Wavy margins
- Prominent midrib
- Sheathing leaf base

SUGARCANE (GANNA):
- Very long linear leaves (50-150 cm)
- Sharp edges that can cut
- Thick prominent midrib
- Arching/drooping habit

BANANA (KELA):
- Huge simple leaves (1-2 meters long)
- Parallel venation with many fine veins
- Midrib very thick
- Leaves tear easily along veins

PAPAYA:
- Large palmate leaves (deeply divided into 7 lobes)
- Lobes are very long and narrow
- Smooth margins
- Long hollow petiole (25-100 cm)
- Grows as crown at top of stem

MANGO (AAM):
- Simple lanceolate leaves
- Leathery texture
- Dark green, glossy upper surface
- Prominent midrib
- Aromatic when crushed
- New leaves are reddish/bronze

GUAVA (AMRUD):
- Simple oval leaves
- Prominent veins (ribbed appearance)
- Leathery texture
- Aromatic when crushed
- Opposite arrangement

ANALYSIS STEPS - FOLLOW STRICTLY:
1. Count leaflets: Are leaves simple (1 piece) or compound (multiple leaflets)?
2. Check leaf edges: Smooth, serrated, or lobed?
3. Measure leaf size: Small, medium, or large?
4. Examine texture: Smooth, rough, hairy?
5. Compare with guidelines above
6. ONLY THEN identify the disease specific to that plant

Common diseases by crop:

PIGEON PEA (TUR):
- Fusarium Wilt (yellowing, wilting from bottom up, vascular browning)
- Sterility Mosaic Disease (mottling, reduced leaf size, stunted growth)
- Alternaria Blight (brown spots with concentric rings on leaves)
- Phytophthora Blight (water-soaked lesions, stem rot)

COTTON:
- Bacterial Blight (angular vein-limited spots, black lesions)
- Alternaria Leaf Spot (circular brown spots with concentric zones)
- Grey Mildew (white powdery growth on underside)
- Verticillium Wilt (yellowing between veins, wilting)

TOMATO:
- Early Blight (dark brown spots with concentric rings - target spot)
- Late Blight (water-soaked spots, white fungal growth on underside)
- Septoria Leaf Spot (small circular spots with gray centers)
- Leaf Curl Virus (upward curling, yellowing, stunted growth)
- Bacterial Spot (small dark spots with yellow halo)

POTATO:
- Late Blight (water-soaked lesions, white mold on underside)
- Early Blight (concentric ring spots on older leaves)
- Verticillium Wilt (yellowing from edges, wilting)

BRINJAL/EGGPLANT:
- Little Leaf Disease (excessive branching, small leaves)
- Bacterial Wilt (sudden wilting without yellowing)
- Phomopsis Blight (circular grey spots with concentric rings)
- Cercospora Leaf Spot (brown spots with yellow halo)

CUCUMBER/SQUASH/PUMPKIN:
- Downy Mildew (angular yellow patches, white/gray growth on underside)
- Powdery Mildew (white powdery coating on upper surface)
- Bacterial Wilt (sudden wilting of entire plant)
- Angular Leaf Spot (angular water-soaked lesions)
- Anthracnose (circular brown spots on leaves and fruits)

CHILI/PEPPER:
- Leaf Curl (upward curling, puckering, stunted growth)
- Cercospora Leaf Spot (circular spots with gray centers)
- Bacterial Leaf Spot (small dark spots with yellow halo)
- Anthracnose (circular sunken lesions on fruits)

OKRA:
- Yellow Vein Mosaic (yellowing along veins, mottling)
- Cercospora Leaf Spot (circular brown spots)
- Powdery Mildew (white powdery coating)

BEAN:
- Rust (orange/brown pustules on underside)
- Anthracnose (dark sunken lesions on pods)
- Common Bacterial Blight (water-soaked spots with yellow halo)
- Bean Common Mosaic (mottling, distortion)

CHICKPEA:
- Ascochyta Blight (grey spots with concentric rings)
- Fusarium Wilt (yellowing, wilting, vascular browning)
- Rust (brown pustules)

ONION/GARLIC:
- Purple Blotch (purple spots with white centers)
- Downy Mildew (pale elongated lesions, fuzzy growth)
- Stemphylium Leaf Blight (small brown spots)

CABBAGE/CAULIFLOWER:
- Black Rot (V-shaped yellowing from leaf margins)
- Downy Mildew (yellow patches with white growth)
- Alternaria Leaf Spot (circular spots with concentric rings)
- Club Root (swollen distorted roots, wilting)

MUSTARD:
- Alternaria Blight (circular grey spots with concentric rings)
- White Rust (white pustules on leaves)
- Downy Mildew (yellow patches)

RICE:
- Blast Disease (diamond-shaped lesions with gray centers)
- Bacterial Leaf Blight (water-soaked to yellow-orange stripes)
- Brown Spot (oval brown spots)
- Sheath Blight (oval greenish-grey lesions on sheath)

WHEAT:
- Rust (yellow, brown, or black pustules)
- Powdery Mildew (white powdery coating)
- Leaf Blight (tan-brown lesions)
- Karnal Bunt (black powdery mass in grains)

MAIZE:
- Common Rust (brown pustules on leaves)
- Turcicum Leaf Blight (long cigar-shaped lesions)
- Maydis Leaf Blight (rectangular lesions)
- Common Smut (large galls on ears)

SUGARCANE:
- Red Rot (red patches with white spots on stalks)
- Smut (black whip-like structures)
- Rust (orange-yellow pustules)

MANGO:
- Anthracnose (black spots on leaves, fruits)
- Powdery Mildew (white powdery coating)
- Bacterial Canker (dark lesions, gum exudation)

BANANA:
- Sigatoka (yellow streaks turning brown-black)
- Panama Wilt (yellowing and wilting of leaves)
- Bunchy Top (dark green streaks, stunted growth)

Response format (JSON):
{
    "plant_type": "specific crop name based on botanical features",
    "plant_identification_confidence": 95,
    "botanical_features_observed": "detailed features that identified the plant - leaf structure, shape, edges, etc.",
    "disease_name": "specific disease identified for THIS plant type",
    "disease_confidence": 85,
    "symptoms_observed": ["symptom1", "symptom2"],
    "severity": "mild/moderate/severe",
    "affected_area": "percentage of leaf area affected"
}

IMPORTANT RULES:
- DO NOT default to Tur/Pigeon Pea - carefully examine actual leaf structure
- Compound leaves with 3 leaflets + smooth edges = Tur
- Large palmate single leaves with lobes = Cucumber/Squash
- Compound leaves with serrated edges = Tomato/Potato
- Match disease ONLY to the identified plant type
- If unsure about plant type, indicate lower plant_identification_confidence

If no disease is detected, return disease_confidence 0 and disease_name as "healthy".
""",
            model=Config.VISION_MODEL
        )
        super().__init__(id=id)
    
    @handler
    async def analyze_image(
        self, 
        image_data: Dict[str, Any], 
        ctx: WorkflowContext[Dict[str, Any]]
    ) -> None:
        """
        Analyze a plant image and identify diseases.
        
        Args:
            image_data: Dictionary containing:
                - image_path: Path to the image file
                - user_id: User identifier
                - additional_context: Any extra info from user
            ctx: Workflow context for sending results to next agent
        """
        image_path = image_data.get("image_path")
        user_context = image_data.get("additional_context", "")
        
        # Load and encode image
        image = Image.open(image_path)
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Create a message with the image
        prompt = f"""Analyze this plant image for disease detection.

CRITICAL FIRST STEP - Plant Identification:
Look at the leaf structure very carefully:

1. Is it a SINGLE leaf with lobes (palmate) OR multiple separate leaflets (compound)?
   - SINGLE LEAF with 3-5 LOBES = Cotton (lobes are connected at base)
   - SEPARATE 3 LEAFLETS on one petiole = Tur/Pigeon Pea (leaflets are completely separate)
   - LARGE SINGLE LEAF with 5-7 LOBES = Cucumber/Squash (much bigger, rough texture)

2. Look at the BASE of the leaf:
   - Heart-shaped base with lobes = Cotton
   - Three separate leaflets meeting at a point = Tur

3. Check leaf SIZE:
   - Cotton: Medium-sized leaves (8-15 cm), lobed
   - Tur: Smaller leaflets (3-7 cm each), three separate pieces
   - Cucumber: Very large leaves (15-25 cm), deeply lobed

4. Examine TEXTURE and EDGES:
   - Cotton: Smooth surface, toothed/serrated margins on lobes
   - Tur: Smooth surface, entire (smooth) margins on leaflets
   - Tomato: Compound with SERRATED leaflets (deeply toothed)

DO NOT confuse:
- Cotton palmate lobed leaves (one piece with lobes) ≠ Tur trifoliate leaves (three separate leaflets)
- Count carefully: Are these lobes of ONE leaf or SEPARATE leaflets?

Additional context from farmer: {user_context}

After accurately identifying the plant type, then analyze for diseases specific to that plant.
Provide detailed diagnosis in JSON format with plant identification reasoning."""
        
        # Create chat message with image content
        message = ChatMessage(
            role="user",
            text=prompt,
            images=[f"data:image/png;base64,{img_base64}"]
        )
        
        # Run the vision agent
        response = await self.agent.run([message])
        diagnosis_text = response.messages[-1].text
        
        # Package the results for the next agent
        result = {
            "image_path": image_path,
            "diagnosis": diagnosis_text,
            "user_id": image_data.get("user_id"),
            "timestamp": image_data.get("timestamp"),
            "additional_context": user_context
        }
        
        # Forward to Research Agent
        await ctx.send_message(result)
    
    def encode_image(self, image_path: str) -> str:
        """
        Encode image to base64 string.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 encoded string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
