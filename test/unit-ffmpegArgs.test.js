const { buildFfmpegArgs } = require("../src/ffmpeg");

test("buildFfmpegArgs GIF", () => {
  const args = buildFfmpegArgs("/tmp/frames", "/tmp/out.gif", {
    fps: 30,
    width: 720,
    height: 0,
    format: "gif",
    scaleStrategy: "lanczos",
    crf: null,
  });
  expect(args).toContain("-framerate");
  expect(args).toContain("30");
  expect(args).toContain("scale=720:-1:flags=lanczos");
  expect(args[args.length - 1]).toBe("/tmp/out.gif");
});

test("buildFfmpegArgs WebM uses vp9 and crf", () => {
  const args = buildFfmpegArgs("/tmp/frames", "/tmp/out.webm", {
    fps: 24,
    width: 640,
    height: 0,
    format: "webm",
    scaleStrategy: "bilinear",
    crf: 33,
  });
  expect(args).toContain("libvpx-vp9");
  expect(args).toContain("33");
  expect(args[args.length - 1]).toBe("/tmp/out.webm");
});

test("buildFfmpegArgs MP4 uses libx264 and crf", () => {
  const args = buildFfmpegArgs("/tmp/frames", "/tmp/out.mp4", {
    fps: 24,
    width: 640,
    height: 0,
    format: "mp4",
    scaleStrategy: "neighbor",
    crf: 20,
  });
  expect(args).toContain("libx264");
  expect(args).toContain("20");
  expect(args[args.length - 1]).toBe("/tmp/out.mp4");
});
