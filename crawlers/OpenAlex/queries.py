"""The two core OpenAlex searches used by --set all."""

START_YEAR = 2019
END_YEAR = 2026

# Set 1: broad generative-haptics context. Set 2: robot-hand bridge.
# Both search titles and abstracts; the client separately applies the years.
CORE_QUERIES = {'1': '("generative haptics" OR "haptic synthesis" OR "tactile synthesis" OR "vibrotactile '
      'generation" OR "haptic generation" OR ((haptic OR tactile OR vibrotactile) AND '
      '("generative model" OR "generative adversarial" OR "diffusion model" OR "flow '
      'matching")) OR (("haptic rendering" OR "tactile rendering" OR "tactile simulation" OR '
      '"tactile simulator") AND ("deep learning" OR "neural network" OR "machine learning" OR '
      '"data-driven")) OR (("tactile signal" OR "tactile image" OR "haptic texture" OR '
      '"tactile texture" OR "haptic feedback") AND (synthesis OR generative)))',
 '2': '("robot hand" OR "robot hands" OR "robotic hand" OR "robotic hands" OR ((robot OR '
      'robotic OR robotics) AND ("dexterous hand" OR "anthropomorphic hand" OR '
      '"multi-fingered hand" OR "multifingered hand"))) AND ("haptic rendering" OR "tactile '
      'rendering" OR "tactile simulation" OR "tactile simulator" OR "tactile sensor '
      'simulation" OR ((tactile OR "tactile sensor") AND ("synthetic data" OR "data '
      'generation" OR "image generation" OR "signal generation" OR "texture synthesis" OR '
      '"generative adversarial" OR "diffusion model")) OR ((tactile OR touch) AND '
      '("sim-to-real" OR "sim2real" OR "simulation to real" OR "domain adaptation") AND '
      '(rendering OR synthesis OR "sensor simulation" OR "tactile images")) OR ((vision OR '
      'visual) AND (tactile OR touch) AND (synthesis OR generative)) OR "simulation of '
      'tactile sensors" OR "model of a tactile skin" OR "tactile sensor model" OR (tactile '
      'AND "sensor model" AND simulation))'}


def compile_queries(selected="all"):
    """Select one or both core searches without modifying their expressions."""
    if selected not in ("all", "1", "2"):
        raise ValueError("Unknown set; choose all, 1, or 2.")
    return [dict(id=f"S{set_id}-core-1", set_id=set_id, role="core",
                 expression=CORE_QUERIES[set_id], search_scope="title_abstract")
            for set_id in ("1", "2") if selected in ("all", set_id)]
