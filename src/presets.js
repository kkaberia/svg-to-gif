module.exports = {
  "crisp-ui": {
    description: "Sharp, clean UI graphics (logos, grids, rectangles).",
    fps: 15,
    scaleStrategy: "neighbor",
    palette: true,
    format: "gif",
    crf: null,
  },
  smooth: {
    description: "Fluid particle motion / animations.",
    fps: 24,
    scaleStrategy: "bilinear",
    palette: true,
    format: "gif",
    crf: null,
  },
  "pixel-art": {
    description: "Pixel art or blocky animations with sharp boundaries.",
    fps: 10,
    scaleStrategy: "neighbor",
    palette: true,
    format: "gif",
    crf: null,
  },
  "hd-video": {
    description: "High-quality video output (MP4).",
    fps: 30,
    scaleStrategy: "lanczos",
    palette: false,
    format: "mp4",
    crf: 18,
  },
};
