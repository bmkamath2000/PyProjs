"""
A small, reusable text box widget for pygame 2.

    pip install pygame
    python textbox.py

Click the box to focus it. Enter submits, Esc quits.
Supports: insertion at the cursor, Backspace/Delete, Left/Right/Home/End,
click-to-position, key repeat, max length, placeholder and horizontal scrolling.
"""
import pygame

BG = (30, 30, 36)
BOX_IDLE = (70, 70, 80)
BOX_ACTIVE = (90, 160, 255)
TEXT = (235, 235, 240)
HINT = (120, 120, 130)

BLINK_MS = 500  # cursor is visible for 500 ms, hidden for 500 ms


class TextBox:
    PAD = 8

    def __init__(self, rect, font, max_length=20, placeholder=""):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.max_length = max_length
        self.placeholder = placeholder
        self.text = ""
        self.cursor = 0          # index in self.text where the caret sits
        self.active = False
        self._scroll = 0         # horizontal pixel offset of the text
        self._blink_start = pygame.time.get_ticks()

    # ---------- helpers ----------
    def _touch(self):
        """Restart the blink cycle so the caret is visible right after input."""
        self._blink_start = pygame.time.get_ticks()

    def _caret_x(self):
        return self.font.size(self.text[: self.cursor])[0]

    def _update_scroll(self):
        """Keep the caret inside the visible area."""
        visible = self.rect.width - 2 * self.PAD
        caret = self._caret_x()
        if caret - self._scroll > visible:
            self._scroll = caret - visible
        elif caret - self._scroll < 0:
            self._scroll = caret
        self._scroll = max(0, self._scroll)

    def _index_at(self, mouse_x):
        """Character index nearest to a mouse x position."""
        x = mouse_x - self.rect.x - self.PAD + self._scroll
        best, best_dist = 0, float("inf")
        for i in range(len(self.text) + 1):
            dist = abs(self.font.size(self.text[:i])[0] - x)
            if dist < best_dist:
                best, best_dist = i, dist
        return best

    # ---------- events ----------
    def handle_event(self, event):
        """Feed every pygame event here. Returns the text when Enter is pressed."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                self.cursor = self._index_at(event.pos[0])
                self._touch()
            return None

        if not self.active:
            return None

        if event.type == pygame.TEXTINPUT:
            # TEXTINPUT already handles shift, layouts and IMEs correctly.
            chunk = "".join(c for c in event.text if c.isprintable())
            chunk = chunk[: self.max_length - len(self.text)]
            if chunk:
                self.text = self.text[: self.cursor] + chunk + self.text[self.cursor:]
                self.cursor += len(chunk)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE and self.cursor > 0:
                self.text = self.text[: self.cursor - 1] + self.text[self.cursor:]
                self.cursor -= 1
            elif event.key == pygame.K_DELETE:
                self.text = self.text[: self.cursor] + self.text[self.cursor + 1:]
            elif event.key == pygame.K_LEFT:
                self.cursor = max(0, self.cursor - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor = min(len(self.text), self.cursor + 1)
            elif event.key == pygame.K_HOME:
                self.cursor = 0
            elif event.key == pygame.K_END:
                self.cursor = len(self.text)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self.text
            else:
                return None
        else:
            return None

        self._touch()
        return None

    # ---------- drawing ----------
    def draw(self, surface):
        pygame.draw.rect(surface, (45, 45, 54), self.rect, border_radius=6)
        pygame.draw.rect(surface, BOX_ACTIVE if self.active else BOX_IDLE,
                         self.rect, width=2, border_radius=6)

        self._update_scroll()
        inner = self.rect.inflate(-2 * self.PAD, -4)
        old_clip = surface.get_clip()
        surface.set_clip(inner)

        if self.text:
            img = self.font.render(self.text, True, TEXT)
        else:
            img = self.font.render(self.placeholder, True, HINT)
        y = self.rect.centery - img.get_height() // 2
        surface.blit(img, (inner.x - self._scroll, y))

        # Blink using elapsed time, so the main loop never has to sleep.
        blink_on = ((pygame.time.get_ticks() - self._blink_start) // BLINK_MS) % 2 == 0
        if self.active and blink_on:
            cx = inner.x - self._scroll + self._caret_x()
            pygame.draw.line(surface, TEXT, (cx, y), (cx, y + img.get_height()), 2)

        surface.set_clip(old_clip)


def main():
    pygame.init()
    screen = pygame.display.set_mode((480, 240))
    pygame.display.set_caption("Text box")
    font = pygame.font.SysFont("segoeui,arial", 24)
    clock = pygame.time.Clock()

    box = TextBox((40, 80, 400, 44), font, max_length=20, placeholder="Type here...")
    box.active = True
    pygame.key.set_repeat(400, 35)   # hold a key to repeat it
    pygame.key.start_text_input()

    submitted = ""
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False
            result = box.handle_event(event)
            if result is not None:
                submitted = result

        screen.fill(BG)
        box.draw(screen)
        if submitted:
            msg = font.render(f"Submitted: {submitted!r} ({len(submitted)} chars)", True, HINT)
            screen.blit(msg, (40, 160))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()