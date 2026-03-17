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
  return result.trim();
}
