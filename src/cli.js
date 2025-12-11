const { parseArgs, loadConfig, mergeOptions, validateOptions, runConversion } = require("./core");

async function main() {
  const started = Date.now();
  try {
    const parsed = parseArgs(process.argv);
    const config = loadConfig(process.cwd());
    const merged = mergeOptions(config, parsed.options);
    const validated = validateOptions(merged);
    await runConversion({
      inputSvg: parsed.inputSvg,
      outputPath: parsed.outputPath,
      ...validated,
    });
    const elapsed = ((Date.now() - started) / 1000).toFixed(2);
    console.error(`Done in ${elapsed}s`);
  } catch (err) {
    console.error("Error:", err && err.message ? err.message : err);
    process.exit(1);
  }
}

module.exports = { main };
