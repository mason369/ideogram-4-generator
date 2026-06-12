import { messages, type Locale } from "./messages";

export { messages, type Locale };

export function translate(locale: Locale, path: string, values?: Record<string, string | number>) {
  const parts = path.split(".");
  let cursor: unknown = messages[locale];
  for (const part of parts) {
    if (!cursor || typeof cursor !== "object" || !(part in cursor)) return path;
    cursor = (cursor as Record<string, unknown>)[part];
  }
  if (typeof cursor !== "string") return path;
  if (!values) return cursor;
  return Object.entries(values).reduce(
    (text, [key, value]) => text.replaceAll(`{${key}}`, String(value)),
    cursor
  );
}
