from urllib.parse import urlsplit, urljoin
import sys
from crawl import crawl_site_async
import asyncio

async def main():

    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) < 3:
        print("no max_concurrency provided")
        sys.exit(1)
    elif len(sys.argv) < 4:
        print("no max_pages provided")
        sys.exit(1)
    elif len(sys.argv) > 4:
        print("too many arguments")
        sys.exit(1)
    else:
        print(f"starting crawl of: {sys.argv[1]}\n Max_concurrency: {sys.argv[2]}\n Max_pages: {sys.argv[3]}\n")

    try:
        result = await crawl_site_async(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

    print(result)
    for key, value in result.items():
        print(value["url"])


if __name__ == "__main__":
    asyncio.run(main())
