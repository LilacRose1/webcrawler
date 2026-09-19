from urllib.parse import urlsplit, urljoin
import sys
from crawl import crawl_site_async
import asyncio

async def main():

    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    else:
        print(f"starting crawl of: {sys.argv[1]}")

    try:
        result = await crawl_site_async(sys.argv[1])
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

    print(result)



if __name__ == "__main__":
    asyncio.run(main())
