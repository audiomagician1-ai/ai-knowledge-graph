/**
 * Text utility functions shared across components.
 */

/**
 * Strip ```choices ... ``` block (complete or partial/in-progress) from LLM content for display.
 * Both LearnPage and ChatPanel use this to clean AI messages before rendering.
 */
export function stripChoicesBlock(text: string): string {
  // First strip complete ```choices ... ``` blocks
  let result = text.replace(/```choices[\s\S]*?```/g, '');
  // Then strip any incomplete/in-progress ```choices block (no closing ```)
  result = result.replace(/```choices[\s\S]*$/g, '');
  // Also strip trailing bullet-point option lists (fallback format from some LLMs)
  // Pattern: "你想了解：\n- option1?\n- option2?" at end of message
  result = result.replace(/(?:^|\n)(?:(?:你想(?:了解|知道)|接下来|你(?:可以)?选择|你(?:更)?想)[^\n]{0,20}[：:]\s*\n)?(?:\s*[-·•*]\s+.+(?:\n|$)){2,5}\s*$/, '');
  return result.trim();
}
