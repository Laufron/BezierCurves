from dataclasses import dataclass
from tkinter import Tk, Canvas, Event, Label, Frame


WINDOW_WIDTH = 700
WINDOW_HEIGHT = 700
MARKER_RADIUS = 7

BG_COLOR = "gray8"
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


def render_bezier_curve(canvas: Canvas, ps: list[Vec2]):
    n = len(control_points)
    canvas.delete("bezier_line")
    if n > 1:
        steps = int(1 / BEZIER_STEP)
        for i in range(steps):
            t1 = i * BEZIER_STEP
            t2 = min(1, (i + 1) * BEZIER_STEP)
            begin = bezier_sample(ps, n, t1)
            end = bezier_sample(ps, n, t2)
            draw_line(canvas, begin, end, color="RED")


def draw_line(canvas: Canvas, begin: Vec2, end: Vec2, color: str):
    canvas.create_line(
        begin.x, begin.y, end.x, end.y, width=2, fill=color, tags="bezier_line"
    )


def draw_marker(
    canvas: Canvas,
    p: Vec2,
    color: str,
    r: int = MARKER_RADIUS,
):
    return canvas.create_oval(
        p.x - r, p.y - r, p.x + r, p.y + r, fill=color, outline="", tags="marker"
    )


def detect_overlapping_control_point(
    canvas: Canvas, user_x: float, user_y: float
) -> int | None:
    items = canvas.find_overlapping(user_x, user_y, user_x, user_y)
    for pid in items:
        if "marker" in canvas.gettags(pid):
            return pid
    return None


if __name__ == "__main__":
    root = Tk()

    frame_labels = Frame(root)
    frame_labels.pack(anchor="w")
    Label(frame_labels, text="Clic gauche : ajoute un point de controle").pack(
        anchor="w"
    )
    Label(frame_labels, text="Clic droit : supprime un point de controle").pack(
        anchor="w"
    )
    Label(frame_labels, text="F1 : Réinitialise la fenêtre").pack(anchor="w")
    Label(frame_labels, text="F2 : Affiche/Masque les points de contrôle").pack(
        anchor="w"
    )
    Label(frame_labels, text="Drag and drop possible").pack(anchor="w")

    canvas = Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=BG_COLOR)
    canvas.pack()

    control_points: list[Vec2] = []
    control_points_pid = {}  # cle = tkinter pid; value = indice dans control_points
    selected_point = None
    show_markers = True

    def clear_all():
        global control_points
        control_points = []
        canvas.delete("all")

    def add_control_point(event: Event):
        global selected_point
        if show_markers:
            overlapping_marker_id = detect_overlapping_control_point(
                canvas, event.x, event.y
            )
            if overlapping_marker_id:
                selected_point = overlapping_marker_id
                return

        p = Vec2(event.x, event.y)
        selected_point = draw_marker(
            canvas, p, color=CONTROL_COLORS if show_markers else BG_COLOR
        )
        global control_points, control_points_pid
        control_points_pid[selected_point] = len(control_points)
        control_points.append(Vec2(event.x, event.y))

        render_bezier_curve(canvas, control_points)

    def on_release(event: Event):
        global selected_point
        selected_point = None

    def on_drag(event: Event):
        if selected_point and show_markers:
            x, y = event.x, event.y
            control_points[control_points_pid[selected_point]] = Vec2(x, y)
            canvas.coords(
                selected_point,
                x - MARKER_RADIUS,
                y - MARKER_RADIUS,
                x + MARKER_RADIUS,
                y + MARKER_RADIUS,
            )
            if len(control_points) > 1:
                render_bezier_curve(canvas, control_points)

    def delete_control_point(event: Event):
        if show_markers:
            overlapping_marker_id = detect_overlapping_control_point(
                canvas, event.x, event.y
            )
            if overlapping_marker_id:
                global control_points, control_points_pid
                removed_index = control_points_pid[overlapping_marker_id]
                control_points.pop(removed_index)
                control_points_pid.pop(overlapping_marker_id)
                for id, index in control_points_pid.items():
                    if index > removed_index:
                        control_points_pid[id] = index - 1

                canvas.delete(overlapping_marker_id)

                render_bezier_curve(canvas, control_points)

    def handle_key_press(event: Event):
        if event.keysym == "F1":
            clear_all()

        if event.keysym == "F2":
            global show_markers
            show_markers = not show_markers
            canvas.itemconfig(
                "marker", fill=CONTROL_COLORS if show_markers else BG_COLOR
            )

    root.bind("<Button-1>", add_control_point)
    root.bind("<ButtonRelease>", on_release)
    root.bind("<B1-Motion>", on_drag)
    root.bind("<Button-2>", delete_control_point)
    root.bind("<Button-3>", delete_control_point)
    root.bind("<KeyPress>", handle_key_press)

    root.mainloop()
