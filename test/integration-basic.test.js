const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const { runConversion } = require("../src/core");

const RUN_INTEGRATION = process.env.SVG_TO_GIF_RUN_INTEGRATION === "1";

const outputs = [];

afterAll(() => {
  for (const file of outputs) {
    try {
      fs.rmSync(file, { force: true });
    } catch {
      // ignore cleanup failures in tests
    }
  }
});

function probeFormat(filePath) {
  const raw = execFileSync(
    "ffprobe",
    [
      "-v",
      "error",
      "-show_entries",
      "format=format_name,duration",
      "-of",
      "json",
      filePath,
    ],
    { encoding: "utf8" },
  );
  const parsed = JSON.parse(raw);
  return parsed.format || {};
}

(RUN_INTEGRATION ? test : test.skip)("converts static SVG to GIF", async () => {
  const input = path.join(__dirname, "fixtures", "static.svg");
  const out = path.join(__dirname, "out-static.gif");
  outputs.push(out);

  await runConversion({
    inputSvg: input,
    outputPath: out,
    duration: 1,
    fps: 5,
    width: 200,
    height: 100,
    scheme: "light",
    format: "gif",
    maxFrames: 2000,
    useGifsicle: false,
    scaleStrategy: "lanczos",
    palette: false,
    crf: null,
    totalFrames: 5,
  });

  expect(fs.existsSync(out)).toBe(true);
  expect(fs.statSync(out).size).toBeGreaterThan(50);
});

(RUN_INTEGRATION ? test : test.skip)("converts static SVG to MP4", async () => {
  const input = path.join(__dirname, "fixtures", "static.svg");
  const out = path.join(__dirname, "out-static.mp4");
  outputs.push(out);

  await runConversion({
    inputSvg: input,
    outputPath: out,
    duration: 1,
    fps: 5,
    width: 200,
    height: 100,
    scheme: "light",
    format: "mp4",
    maxFrames: 2000,
    useGifsicle: false,
    scaleStrategy: "lanczos",
    palette: false,
    crf: 20,
    totalFrames: 5,
  });

  expect(fs.existsSync(out)).toBe(true);
  expect(fs.statSync(out).size).toBeGreaterThan(200);
  const meta = probeFormat(out);
  expect((meta.format_name || "").includes("mp4")).toBe(true);
  const dur = parseFloat(meta.duration);
  expect(dur).toBeGreaterThan(0.5);
  expect(dur).toBeLessThan(1.5);
});

(RUN_INTEGRATION ? test : test.skip)("converts static SVG to WebM", async () => {
  const input = path.join(__dirname, "fixtures", "static.svg");
  const out = path.join(__dirname, "out-static.webm");
  outputs.push(out);

  await runConversion({
    inputSvg: input,
    outputPath: out,
    duration: 1,
    fps: 5,
    width: 200,
    height: 100,
    scheme: "light",
    format: "webm",
    maxFrames: 2000,
    useGifsicle: false,
    scaleStrategy: "lanczos",
    palette: false,
    crf: 30,
    totalFrames: 5,
  });

  expect(fs.existsSync(out)).toBe(true);
  expect(fs.statSync(out).size).toBeGreaterThan(200);
  const meta = probeFormat(out);
  expect(
    (meta.format_name || "").includes("webm") ||
      (meta.format_name || "").includes("matroska"),
  ).toBe(true);
  const dur = parseFloat(meta.duration);
  expect(dur).toBeGreaterThan(0.5);
  expect(dur).toBeLessThan(1.5);
});
