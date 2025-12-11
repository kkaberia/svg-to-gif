const { validateOptions, DEFAULTS } = require("../src/core");

test("validateOptions rejects invalid fps", () => {
  expect(() =>
    validateOptions({
      duration: 2,
      fps: 0,
      width: 200,
      height: 0,
      scheme: "light",
      format: "gif",
      maxFrames: 2000,
      useGifsicle: true,
      scaleStrategy: "lanczos",
      palette: false,
      crf: null,
    })
  ).toThrow();
});

test("validateOptions computes totalFrames and defaults", () => {
  const v = validateOptions({
    duration: 2,
    fps: 10,
    width: 200,
    height: 0,
    scheme: "light",
    format: "gif",
    maxFrames: 2000,
    useGifsicle: true,
    scaleStrategy: "lanczos",
    palette: true,
    crf: null,
  });
  expect(v.totalFrames).toBe(20);
  expect(v.maxFrames).toBe(2000);
  expect(v.palette).toBe(true);
});
