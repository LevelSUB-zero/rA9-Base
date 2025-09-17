def frame_output(answer, tone="neutral"):
    if tone == "emotional":
        return f"🧡 {answer}"
    elif tone == "logical":
        return f"🧠 {answer}"
    elif tone == "creative":
        return f"🌌 {answer}"
    elif tone == "strategic":
        return f"🚀 {answer}"
    return answer