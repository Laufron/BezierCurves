from dataclasses import dataclass
from tkinter import Tk, Canvas, Event


WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700

CONTROL_COLORS = "medium sea green"

BEZIER_STEP = 0.01


@dataclass
class Vec2:
    x: float
    y: float


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerpv2(p1: Vec2, p2: Vec2, t: float) -> Vec2:
    return Vec2(lerp(p1.x, p2.x, t), lerp(p1.y, p2.y, t))


def bezier_sample(ps: list[Vec2], n: int, t: float) -> Vec2:
    xs = ps.copy()
    while n > 1:
        for i in range(n - 1):
            xs[i] = lerpv2(xs[i], xs[i + 1], t)
        n -= 1
    return xs[0]


def render_bezier_curve(canvas: Canvas, ps: list[Vec2], n: int) -> list:
    steps = int(1 / BEZIER_STEP)
    lines_id = []
    for i in range(steps):
        t1 = i * BEZIER_STEP
        t2 = min(1, (i + 1) * BEZIER_STEP)
        begin = bezier_sample(ps, n, t1)
        end = bezier_sample(ps, n, t2)
        seg = draw_line(canvas, begin, end, color="RED")
        lines_id.append(seg)
    return lines_id


def draw_line(canvas: Canvas, begin: Vec2, end: Vec2, color: str):
    return canvas.create_line(begin.x, begin.y, end.x, end.y, width=2, fill=color)


def draw_marker(
    canvas: Canvas,
    p: Vec2,
    color: str,
    r: int = 7,
):
    canvas.create_oval(p.x - r, p.y - r, p.x + r, p.y + r, fill=color, outline="")


if __name__ == "__main__":
    root = Tk()
    canvas = Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="gray8")
    canvas.pack()

    control_points: list[Vec2] = []
    n = 0
    lines = []

    def clear_all():
        global control_points, n, lines
        control_points = []
        n = 0
        lines = []
        canvas.delete("all")

    def add_control_point(event: Event):
        global control_points, lines, n
        p = Vec2(event.x, event.y)
        draw_marker(canvas, p, color=CONTROL_COLORS)
        control_points.append(Vec2(event.x, event.y))
        n += 1
        if n > 1:
            if lines:
                for l in lines:
                    canvas.delete(l)
            lines = render_bezier_curve(canvas, control_points, n)

    def drag_handler(event: Event):
        print(event.x, event.y)
    
    def handle_key_press(event: Event):
        if event.keysym == "F1":
            clear_all()

    root.bind("<Button-1>", add_control_point)
    # root.bind("<B1-Motion>", drag_handler)
    root.bind("<KeyPress>", handle_key_press)

    root.mainloop()
