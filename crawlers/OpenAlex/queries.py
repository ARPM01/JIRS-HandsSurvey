"""Current recommended searches and optional diagnostic topic blocks."""

START_YEAR = 2019

END_YEAR = 2026

# Robot-hand embodiment condition for Set 2 diagnostic searches. Accepts direct
# robot/robotic-hand phrases, or alternative hand descriptions accompanied by
# robot/robotic/robotics. Generic hands or grippers alone do not qualify.
# The Set 2 core query below contains the same condition as literal text;
# changing HAND does not automatically change CORE_QUERIES["2"].
HAND = ('("robot hand" OR "robot hands" OR "robotic hand" OR "robotic hands" OR ((robot OR robotic '
 'OR robotics) AND ("dexterous hand" OR "anthropomorphic hand" OR "multi-fingered hand" OR '
 '"multifingered hand")))')

# Generative/computational-output terms added to broader Set 1 topic searches
# (S1-02 and S1-05 through S1-08). This prevents an individual diagnostic search
# from retrieving all rendering, wearable, perception, or interaction work.
# Not added in --context mode; S1-01, S1-03, and S1-04 already target synthesis.
# This helper does not alter the independently written CORE_QUERIES.
GEN = ('(generative OR synthesis OR generation OR prediction OR "generative adversarial network" OR '
 '"diffusion model")')

# Original topic-level Boolean expressions: S1-01..08 cover broad haptics;
# S2-01..07 cover the robot-hand/generative-haptics bridge. Used by --topic
# (e.g. --topic S2-04) and --context for diagnosis and background exploration.
# compile_queries adds HAND or GEN where appropriate and combines/splits
# selected blocks into requests. Normal core runs do not execute these blocks;
# their IDs are recorded as topic coverage metadata, not proven per-paper hits.
TOPIC_BLOCKS = {'S1-01': '(haptic OR haptics) AND (generative OR generation OR synthesis)',
 'S1-02': '"haptic rendering" OR "haptics rendering" OR (haptic AND rendering)',
 'S1-03': '"tactile synthesis" OR (tactile AND synthesis)',
 'S1-04': '("haptic feedback" OR "tactile feedback" OR "vibrotactile feedback") AND '
          '(synthesis OR generation OR generative)',
 'S1-05': '(wearable OR wearables) AND (haptic OR haptics OR tactile OR vibrotactile) AND (AI '
          'OR "artificial intelligence" OR "machine learning" OR "deep learning" OR "neural '
          'network")',
 'S1-06': '(multimodal OR "multi-modal" OR "cross-modal") AND (haptic OR haptics OR tactile) '
          'AND perception',
 'S1-07': '(haptic OR haptics) AND (AI OR "artificial intelligence" OR "machine learning" OR '
          '"deep learning" OR "neural network")',
 'S1-08': '(embodied OR embodiment) AND (haptic OR haptics OR tactile) AND interaction',
 'S2-01': '(robot OR robotic OR robotics) AND (tactile OR touch) AND (data OR signal OR '
          'sensing OR sensor) AND ("haptic rendering" OR "tactile rendering" OR ((haptic OR '
          'tactile) AND rendering))',
 'S2-02': '(tactile OR touch OR "tactile sensing") AND ("sim-to-real" OR "sim to real" OR '
          '"simulation-to-real" OR "simulation to real" OR "simulation to reality" OR '
          '("domain adaptation" AND (simulation OR synthetic)))',
 'S2-03': '(tactile OR "vision-based tactile" OR "optical tactile") AND (sensor OR sensing) '
          'AND ("synthetic data" OR "data synthesis" OR "data generation" OR "synthetic '
          'image" OR "synthetic tactile")',
 'S2-04': '(tactile OR "tactile sensor") AND (simulation OR simulator) AND (learned OR '
          'learning OR neural OR "data-driven" OR differentiable)',
 'S2-05': '("vision-to-touch" OR "vision to touch" OR "visual-to-tactile" OR "visual to '
          'tactile" OR "image-to-tactile" OR ((vision OR visual OR image) AND (touch OR '
          'tactile) AND ("cross-modal" OR crossmodal OR multimodal))) AND (generation OR '
          'synthesis OR generative OR translation)',
 'S2-06': 'tactile AND (signal OR signals OR time-series OR "time series") AND (generation OR '
          'synthesis OR generative) AND ("deep learning" OR "neural network" OR "generative '
          'model" OR diffusion OR transformer OR autoencoder OR GAN)',
 'S2-07': '(tactile OR haptic OR haptics) AND texture AND (synthesis OR generation OR '
          'generative) AND (GAN OR GANs OR "generative adversarial network" OR "generative '
          'adversarial networks" OR "adversarial learning")'}

# Complete, empirically refined searches used by normal runs, including
# --pilot, when neither --topic nor --context is supplied. Keys "1" and "2"
# select the broad field context and robot-hand bridge sets, respectively.
# These literal expressions are maintained independently of the helpers and
# topic blocks above; edits to those constants do not rebuild the core queries.
# Both use title/abstract search; the client separately applies 2019–2026.
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

def compile_queries(selected="all", context=False, topic=None):
    """Compile safe OR chunks, retaining the hand condition on every branch."""
    from urllib.parse import quote_plus

    blocks = TOPIC_BLOCKS
    if not context and not topic:
        return [dict(id=f"S{set_id}-core-1", set_id=set_id, role="core",
                     expression=CORE_QUERIES[set_id], search_scope="title_abstract",
                     topic_blocks=[k for k in blocks if k.startswith("S" + set_id)])
                for set_id in ("1", "2") if selected in ("all", set_id)]
    if context and selected != "1":
        raise ValueError("Context pilots require --set 1.")
    if topic and topic not in blocks:
        raise ValueError("Unknown topic ID.")
    queries = []
    for set_id in ("1", "2"):
        if selected not in ("all", set_id):
            continue
        ids = [k for k in blocks if k.startswith("S" + set_id)]
        if context:
            ids = [k for k in ids if k not in ("S1-01", "S1-03", "S1-04")]
        if topic:
            ids = [k for k in ids if k == topic]
        branches = []
        for key in ids:
            expression = blocks[key]
            if set_id == "2":
                hand = HAND
                expression = f"{hand} AND ({expression})"
            elif not context and key not in ("S1-01", "S1-03", "S1-04"):
                expression = f"({expression}) AND {GEN}"
            branches.append((key, f"({expression})"))
        chunks = []
        for key, expression in branches:
            if not chunks or (len(quote_plus(" OR ".join(chunks[-1][1] + [expression]))) > 2800
                                  or len(" OR ".join(chunks[-1][1] + [expression])) > 1400):
                chunks.append(([], []))
            chunks[-1][0].append(key)
            chunks[-1][1].append(expression)
        for n, (keys, expressions) in enumerate(chunks, 1):
            query = " OR ".join(expressions)
            if len(quote_plus(query)) > 2800 or len(query) > 1400:
                raise ValueError("A topic exceeds the request size budget; split its block.")
            queries.append(dict(id=f"S{set_id}-{('context' if context else 'core')}-{n}",
                                set_id=set_id, role="context" if context else "core",
                                topic_blocks=keys, expression=query))
    if not queries:
        raise ValueError("No topics match the selected set.")
    for query in queries:
        query["search_scope"] = "title_abstract"
    return queries
