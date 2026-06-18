def detect_triple_riding(
    detections
):

    rider_count = 0

    motorcycle_found = False

    for det in detections:

        if det["class_name"] == "motorcycle":
            motorcycle_found = True

        if det["class_name"] == "person":
            rider_count += 1

    if motorcycle_found and rider_count > 2:

        return {
            "violation": True,
            "riders": rider_count
        }

    return {
        "violation": False,
        "riders": rider_count
    }