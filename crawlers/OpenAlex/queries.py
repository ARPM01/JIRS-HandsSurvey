"""Literature searches supporting a survey of biological and robotic hands.

Set 1 supplies broad generative-haptics context; Set 2 collects methods that
could connect this field to robotic hands. Together they support analysis of
which sensing and interaction gaps generative haptics might address. They do
not exhaustively cover biological hand function or robotic hardware/control;
those comparisons also require separately collected baseline literature.

``python main.py --set all`` submits both expressions as separate searches.
``--set 1`` and ``--set 2`` select them individually; ``--pilot`` uses the same
expressions with sampled retrieval. The client searches titles and abstracts
and applies the publication-year range below. Results are exported separately,
deduplicated by OpenAlex ID within each set; shared papers remain in both.

These are candidate-retrieval sets, not final inclusion decisions. Screening
must distinguish generated tactile outputs from ordinary recognition, control,
sensor fabrication, and incidental mentions of touch. These expressions adopt
the tighter candidates documented in query_review_20260909_194845_f77afc.md.
Use a fresh run directory after changing queries; saved runs are not refiltered.
"""

START_YEAR = 2019
END_YEAR = 2026

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
}


def compile_queries(selected="all"):
    """Select one or both core searches without modifying their expressions."""
    if selected not in ("all", "1", "2"):
        raise ValueError("Unknown set; choose all, 1, or 2.")
    return [dict(id=f"S{set_id}-core-1", set_id=set_id, role="core",
                 expression=CORE_QUERIES[set_id], search_scope="title_abstract")
            for set_id in ("1", "2") if selected in ("all", set_id)]
