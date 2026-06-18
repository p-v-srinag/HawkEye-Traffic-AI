from app.modules.violations.triple_riding import (
    detect_triple_riding
)


def evaluate(
    detections
):

    violations = []

    triple = detect_triple_riding(
        detections
    )

    if triple["violation"]:

        violations.append(
            {
                "type":
                "TRIPLE_RIDING",

                "riders":
                triple["riders"]
            }
        )

    return violations