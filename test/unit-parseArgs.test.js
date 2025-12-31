const { parseArgs } = require("../src/core");

test("parseArgs extracts basic flags and preset", () => {
  const { inputSvg, outputPath, options } = parseArgs([
    "node",
    "cli",
    "in.svg",
    "out.gif",
    "--duration",
    "5",
    "--fps",
    "24",
    "--width",
    "800",
    "--scheme",
    "dark",
    "--format",
    "webm",
    "--preset",
    "smooth",
    "--scale-strategy",
    "neighbor",
    "--palette",
    "--crf",
    "32",
    "--no-gifsicle",
  ]);

  expect(inputSvg.endsWith("in.svg")).toBe(true);
  expect(outputPath.endsWith("out.gif")).toBe(true);
  expect(options.duration).toBe(5);
  expect(options.fps).toBe(24);
  expect(options.width).toBe(800);
  expect(options.scheme).toBe("dark");
  expect(options.format).toBe("webm");
  expect(options.preset).toBe("smooth");
  expect(options.scaleStrategy).toBe("neighbor");
  expect(options.palette).toBe(true);
  expect(options.crf).toBe(32);
  expect(options.useGifsicle).toBe(false);
});
