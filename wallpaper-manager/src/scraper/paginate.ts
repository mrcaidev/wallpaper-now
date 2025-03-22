export type Page = {
  index: number;
  size: number;
};

export function paginate(total: number, maxPageSize: number) {
  const fullPageCount = Math.floor(total / maxPageSize);
  const remainder = total % maxPageSize;

  const pages = Array.from(
    { length: fullPageCount },
    (_, i) => ({ index: i + 1, size: maxPageSize }) as Page,
  );

  if (remainder > 0) {
    pages.push({ index: fullPageCount + 1, size: remainder });
  }

  return pages;
}
