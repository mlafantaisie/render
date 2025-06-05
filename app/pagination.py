def get_pagination_window(current_page, total_pages, window=3):
    """
    Returns list of page numbers to display in pagination window.
    """
    pages = []

    # Always show first page
    pages.append(1)

    # Pages before and after current
    start = max(current_page - window, 2)
    end = min(current_page + window, total_pages - 1)

    if start > 2:
        pages.append("...")

    pages.extend(range(start, end + 1))

    if end < total_pages - 1:
        pages.append("...")

    # Always show last page
    if total_pages > 1:
        pages.append(total_pages)

    return pages
