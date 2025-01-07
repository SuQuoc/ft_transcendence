import httpx

# Dependency to other Microservice
async def get_displayname(cookie_dict):
    if not cookie_dict:
        raise Exception('No cookie provided')
    cookie = httpx.Cookies(cookie_dict)
    headers = {
        'Content-Type': 'application/json',
    }
    async with httpx.AsyncClient() as client:
        response = await client.get("http://usermanagement:8000/um/profile", headers=headers, cookies=cookie_dict) # NOTE: fetches more then just the name
        if response.status_code != 200:
            raise Exception('Error getting displayname from UM')
        return response.json().get("displayname")