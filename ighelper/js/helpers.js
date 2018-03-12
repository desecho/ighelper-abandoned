export function param(params) {
  const paramsOutput = new URLSearchParams();
  for (const key in params) {
    if (params.hasOwnProperty(key)) {
      paramsOutput.append(key, params[key]);
    }
  }
  return paramsOutput;
}
