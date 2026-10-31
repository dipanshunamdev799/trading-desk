import type { ISeriesPrimitive, ISeriesPrimitivePaneView, SeriesAttachedParameter, UTCTimestamp } from "lightweight-charts";
import type { CanvasRenderingTarget2D } from "fancy-canvas";
import { studyColor, type StudyOverlay } from "@/lib/priceAction";

/** Draw in the price pane so bands and lines follow zoom, pan and price scaling. */
export class PriceActionOverlay implements ISeriesPrimitive {
  private attachedTo: SeriesAttachedParameter | null = null;
  private view: ISeriesPrimitivePaneView = { zOrder: () => "bottom", renderer: () => ({ draw: target => this.draw(target) }) };
  constructor(private overlay: StudyOverlay) {}
  attached(param: SeriesAttachedParameter) { this.attachedTo = param; param.requestUpdate(); }
  detached() { this.attachedTo = null; }
  paneViews() { return [this.view]; }
  private draw(target: CanvasRenderingTarget2D) {
    const api = this.attachedTo;
    if (!api) return;
    const x = (ts: string) => api.chart.timeScale().timeToCoordinate((Date.parse(ts) / 1000) as UTCTimestamp);
    const y = (value: number) => api.series.priceToCoordinate(value);
    target.useMediaCoordinateSpace(({ context: ctx, mediaSize }) => {
      ctx.save(); ctx.beginPath(); ctx.rect(0, 0, mediaSize.width, mediaSize.height); ctx.clip();
      for (const zone of this.overlay.zones) {
        const left = x(zone.start), right = x(zone.end), top = y(zone.high), bottom = y(zone.low);
        if (left == null || right == null || top == null || bottom == null) continue;
        const color = studyColor(zone.side);
        ctx.fillStyle = color + (zone.active ? "18" : "0b");
        ctx.strokeStyle = color + "66"; ctx.lineWidth = 1; ctx.setLineDash(zone.tested ? [3, 3] : []);
        ctx.fillRect(left, top, Math.max(right-left, 3), bottom-top);
        ctx.strokeRect(left, top, Math.max(right-left, 3), bottom-top);
      }
      const labelPositions: number[] = [];
      for (const line of this.overlay.lines) {
        ctx.strokeStyle = line.concept === 7 || line.concept === 8 ? "#86B8F6" : studyColor(line.side);
        ctx.lineWidth = line.concept === 12 ? .7 : 1.2;
        ctx.setLineDash(line.concept === 9 ? [] : line.concept === 12 ? [2, 6] : [5, 4]);
        ctx.beginPath(); let started = false;
        for (const point of line.points) {
          const px = x(point.ts), py = y(point.value);
          if (px == null || py == null) continue;
          if (started) ctx.lineTo(px, py); else ctx.moveTo(px, py);
          started = true;
        }
        ctx.stroke();
        const last = line.points.at(-1);
        const lastY = last ? y(last.value) : null;
        if (last && lastY != null && lastY > 12 && lastY < mediaSize.height-14 && !labelPositions.some(py => Math.abs(py-lastY) < 13)) {
          labelPositions.push(lastY);
          ctx.font = "10px ui-monospace, monospace"; ctx.textAlign = "right";
          const label = `${line.label} ${last.value.toFixed(2)}`;
          ctx.fillStyle = "#121820dd";
          ctx.fillRect(mediaSize.width-ctx.measureText(label).width-12, lastY-12, ctx.measureText(label).width+10, 13);
          ctx.fillStyle = ctx.strokeStyle; ctx.fillText(label, mediaSize.width-6, lastY-2);
        }
      }
      ctx.restore();
    });
  }
}
