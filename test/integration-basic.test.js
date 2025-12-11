const fs = require("fs");
const path = require("path");
const { runConversion } = require("../src/core");

const RUN_INTEGRATION = process.env.SVG_TO_GIF_RUN_INTEGRATION === "1";

(RUN_INTEGRATION ? test : test.skip)("converts static SVG to GIF", async () => {
  const input = path.join(__dirname, "fixtures", "static.svg");
  const out = path.join(__dirname, "out-static.gif");

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
