"""Literature searches supporting a survey of biological and robotic hands.

Set 1 supplies broad generative-haptics context; Set 2 collects methods that
could connect this field to robotic hands. Together they support analysis of
which sensing and interaction gaps generative haptics might address. They do
not exhaustively cover biological hand function or robotic hardware/control;
those comparisons also require separately collected baseline literature.

Set 3 mirrors the IEEE foundation-model/agentic-AI search for robotic hands
and manipulation.

``python main.py --set all`` submits all three expressions separately.
``--set 1``, ``--set 2`` and ``--set 3`` select them individually; ``--pilot`` uses the same
expressions with sampled retrieval. The client searches titles and abstracts
and applies the publication-year range below. Results are exported separately,
deduplicated by OpenAlex ID within each set; shared papers remain in each matching set.

These are candidate-retrieval sets, not final inclusion decisions. Screening
must distinguish generated tactile outputs from ordinary recognition, control,
sensor fabrication, and incidental mentions of touch. Sets 1 and 2 adopt
the tighter candidates documented in query_review_20260909_194845_f77afc.md.
Use a fresh run directory after changing queries; saved runs are not refiltered.
"""

START_YEAR = 2019
END_YEAR = 2026

# SET 3 mirrors the IEEE crawler Boolean expression and terminology.
EMBODIMENT_QUERY = (
    '("robotic hand" OR "robot hand" OR "dexterous hand" OR '
    '"anthropomorphic hand" OR "artificial hand" OR '
    '"prosthetic hand" OR "bionic hand" OR '
    '"multifingered hand" OR "multi-fingered hand" OR '
    '"multifinger hand" OR "multi-finger hand" OR '
    '"five-finger hand" OR "five-fingered hand" OR '
    '"robotic palm" OR "robotic finger" OR '
    '"soft robotic hand" OR "tendon-driven hand" OR '
    '"multifingered gripper" OR "multi-fingered gripper" OR '
    '"dexterous gripper" OR "hand morphology" OR '
    '"finger synergy" OR "hand synergy" OR '
    '"dexterous grasp" OR "multifinger grasp" OR '
    '"multi-finger grasp")'
)

MANIPULATION_QUERY = (
    '(grasping OR "grasp generation" OR "functional grasping" OR '
    '"task-oriented grasping" OR "dexterous manipulation" OR '
    '"in-hand manipulation" OR "in hand manipulation" OR '
    '"object manipulation" OR "hand-object interaction" OR '
    '"finger control" OR "hand control")'
)

FOUNDATION_MODEL_QUERY = (
    '("foundation model" OR "foundation models" OR '
    '"robot foundation model" OR "robotics foundation model" OR '
    '"multimodal foundation model" OR '
    '"vision foundation model" OR "visual foundation model" OR '
    '"promptable foundation model" OR '
    '"large language model" OR LLM OR '
    '"vision-language model" OR "visual language model" OR VLM OR '
    '"vision-language-action model" OR "vision-language-action" OR '
    '"vision language action model" OR VLA OR '
    '"multimodal language model" OR '
    '"large multimodal model" OR '
    '"multimodal large language model" OR MLLM OR '
    '"vision-language policy" OR "multimodal policy" OR '
    '"generalist policy" OR "generalist robot policy" OR '
    '"general-purpose robot policy" OR '
    '"language-conditioned policy" OR '
    '"language-conditioned manipulation" OR '
    '"open-vocabulary manipulation" OR '
    '"tactile-language-action" OR '
    '"vision-language-tactile-action" OR '
    '"latent action representation")'
)

AGENTIC_QUERY = (
    '("agentic AI" OR '
    '"LLM-based planning" OR "LLM planner" OR '
    '"language-model-based planning" OR '
    '"VLM-based planning" OR "VLM planner" OR '
    '"vision-language planning" OR "multimodal planner" OR '
    '"language-guided planning" OR '
    '"language-guided task planning" OR '
    '"open-world planning" OR "task decomposition" OR '
    '"chain-of-thought" OR "robot chain-of-thought" OR '
    '"self-evaluation" OR "self-reflection" OR '
    '"reflection-based planning" OR '
    '"closed-loop reasoning" OR '
    '"autonomous reasoning" OR "reasoning-based manipulation" OR '
    '"failure recovery" OR "recovery mechanism")'
)

FOUNDATION_AGENTIC_QUERY = (
    f"(({EMBODIMENT_QUERY}) OR ({MANIPULATION_QUERY})) AND "
    f"(({FOUNDATION_MODEL_QUERY}) OR ({AGENTIC_QUERY}))"
)

CORE_QUERIES = {
    # SET 1 — Broad generative-haptics context for virtual/physical interaction.
    # Require explicit tactile output or learned rendering/force feedback.
    # Prediction is tied to tactile signals, touch or skin vibration; generic
    # neural prediction and unrelated "next-generation" wording do not suffice.
    # No robot condition: wearable, human-facing and cross-modal methods can
    # provide transferable context. Screen for what the model actually outputs.
    "1": (
        '( "generative haptics" OR "haptic synthesis" OR "tactile synthesis" OR "haptic '
        'generation" OR "tactile generation" OR "vibrotactile generation" OR "haptic texture '
        'generation" OR "tactile image generation" OR "tactile signal generation" OR "tactile '
        'prediction" OR "haptic signal prediction" OR "tactile signal prediction" OR (("haptic '
        'signal" OR "tactile signal" OR "tactile image" OR "haptic texture" OR "tactile texture" '
        'OR "haptic feedback" OR "tactile feedback" OR "tactile display" OR "haptic rendering" OR '
        '"tactile rendering") AND ("generative model" OR "generative adversarial" OR "diffusion '
        'model" OR "flow matching")) OR (("haptic rendering" OR "tactile rendering" OR "haptic '
        'prediction") AND ("machine learning" OR "deep learning" OR neural OR "data-driven" OR '
        'learned)) OR (("haptic signal" OR "tactile signal" OR "tactile image" OR "haptic '
        'texture" OR "tactile texture") AND (synthesis OR "synthetic data") AND (model OR '
        'learning OR sensor OR rendering OR display)) OR ("haptic feedback" AND ("force '
        'prediction" OR "force estimation") AND ("data-driven" OR learned OR "deep learning" OR '
        '"machine learning")) OR ((haptic OR tactile OR "touch-elicited") AND ("world model" OR '
        '"predicting touch" OR "predicting skin vibrations")) )'
    ),
    # SET 2 — Computational touch methods applicable to robotic hands.
    # Every branch requires robotics or tactile-sensor context, including
    # vision-to-touch generation. A complete robot-hand demo is not mandatory.
    # Covers tactile/optical simulation, synthetic observations, tactile
    # sim-to-real transfer, generative outputs and predictive world models.
    # Retains tactile super-resolution and biomimetic afferent/spike generation
    # for the biological comparison. Generic sensor-design simulation alone
    # is insufficient outside the deliberately retained optical-sensor branch.
    # Screen whether evaluation uses a hand, gripper, isolated sensor or only
    # simulation; retrieval does not establish biological-level capability.
    "2": (
        '( (robot OR robotic OR robotics OR "tactile sensor" OR "vision-based tactile" OR '
        '"optical tactile" OR "touch sensor") AND ( "tactile simulation" OR "tactile simulator" '
        'OR "simulation of tactile sensors" OR (("vision-based tactile" OR "optical tactile") AND '
        '(simulation OR simulator)) OR ((haptic OR tactile) AND (simulation OR simulator) AND '
        '(rendering OR "synthetic data" OR "image generation" OR "signal generation")) OR '
        '((haptic OR tactile) AND ("sim-to-real" OR sim2real OR "domain adaptation" OR "domain '
        'randomization") AND (simulation OR rendering OR "synthetic data" OR "simulated '
        'measurements" OR "image translation")) OR (("tactile signal" OR "tactile image" OR '
        '"haptic texture" OR "tactile texture" OR "tactile display") AND (synthesis OR '
        '"generative model" OR "generative adversarial" OR "diffusion model" OR "flow matching")) '
        'OR "tactile generation" OR "haptic generation" OR "haptic texture generation" OR '
        '"tactile image generation" OR "tactile signal generation" OR (("vision-to-touch" OR '
        '"visual-to-tactile" OR "cross-modal") AND ("haptic rendering" OR "tactile synthesis" OR '
        '"tactile generation")) OR "tactile prediction" OR ((tactile OR "visuo-tactile") AND '
        '"world model") OR (tactile AND ("super-resolution" OR "afferent spike generation" OR '
        '"spike train generation")) ) )'
    ),
    "3": FOUNDATION_AGENTIC_QUERY,
}


def compile_queries(selected="all"):
    """Select one or all core searches without modifying their expressions."""
    if selected != "all" and selected not in CORE_QUERIES:
        raise ValueError("Unknown set; choose all, 1, 2, or 3.")
    return [dict(id=f"S{set_id}-core-1", set_id=set_id, role="core",
                 expression=CORE_QUERIES[set_id], search_scope="title_abstract")
            for set_id in CORE_QUERIES if selected in ("all", set_id)]
