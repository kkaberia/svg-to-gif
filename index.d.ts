export interface SvgToGifOptions {
  duration?: number;
  fps?: number;
  width?: number;
  height?: number;
  scheme?: "light" | "dark";
  format?: "gif" | "webm" | "mp4";
  maxFrames?: number;
  useGifsicle?: boolean;
  scaleStrategy?: "lanczos" | "bilinear" | "neighbor";
  palette?: boolean;
  crf?: number | null;
  preset?: "crisp-ui" | "smooth" | "pixel-art" | "hd-video" | string;
}

export interface ValidatedOptions {
  duration: number;
  fps: number;
  width: number;
  height: number;
  scheme: "light" | "dark";
  format: "gif" | "webm" | "mp4";
  maxFrames: number;
  useGifsicle: boolean;
  scaleStrategy: "lanczos" | "bilinear" | "neighbor";
  palette: boolean;
  crf: number | null;
  totalFrames: number;
}

export function parseArgs(argv: string[]): {
  inputSvg: string;
  outputPath: string;
  options: SvgToGifOptions;
};

export function loadConfig(cwd: string): Partial<SvgToGifOptions>;

export function mergeOptions(
  config: Partial<SvgToGifOptions>,
  cliOptions: SvgToGifOptions
): SvgToGifOptions & { maxFrames: number; useGifsicle: boolean };

export function validateOptions(opts: SvgToGifOptions): ValidatedOptions;

export function runConversion(params: {
  inputSvg: string;
  outputPath: string;
} & ValidatedOptions): Promise<void>;
