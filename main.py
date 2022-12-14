import asyncio, random, datetime, requests, json
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError 
from components import proxyfy


def genderize(name):
  req = requests.get(f"https://api.genderize.io/?name={name}").text
  return eval(req)["gender"].title()


def ziptostate(zip):
  req = requests.get(f"https://api.zippopotam.us/us/{zip}").text
  return eval(req)["places"][0]["state"]


def playwright_devices():
  req = requests.get("https://raw.githubusercontent.com/microsoft/playwright/main/packages/playwright-core/src/server/deviceDescriptorsSource.json").text
  return open("devices.txt").read().split("\n"), json.loads(req)

async def emulated_browser(playwright, proxy=None):
  playwright_device_list = playwright_devices()
  device_list = playwright_device_list[0]

  random_device = random.choice(device_list)
  # print(random_device)
  yield random_device
  # random_device = device_list[9]
  
  device = playwright.devices[random_device]
  # device.pop("viewport")
  # print(device)
  # system = 
  # browser = await playwright.chromium.launch(headless=False)
  browser = await playwright[playwright_device_list[1][random_device]["defaultBrowserType"]].launch(headless=False)
  
  yield await browser.new_context(**device, 
    proxy={**proxy} if proxy else None,
    # viewport={"width": 800, "height": 900}
  )
  
  

async def random_selector(page, selector):
  item = await page.query_selector_all(f'{selector} > option')
  item = item[1:]
  item = random.choice(item)
  item = await item.get_attribute('value')
  await page.select_option(selector, item)
  return item


async def scroller(page, wait):
  while wait > 0:
      print('AU')
      about_us = await page.query_selector('#kool')
      await about_us.scroll_into_view_if_needed()
      rem = random.randint(2000, 5000)
      await page.wait_for_timeout(rem)
      wait -= rem
      print("foot")
      foot = await page.query_selector('footer')
      await foot.scroll_into_view_if_needed()
      rem = random.randint(2000, 5000)
      await page.wait_for_timeout(rem)
      wait -= rem


async def main(first_name, last_name, street_address, city, zipp, phone, email):
  async with async_playwright() as p:
    device_setting = emulated_browser(
      p, 
      proxy=proxyfy(zipp, city)
    )
    random_device = await device_setting.__anext__()
    print(random_device)
    browser = await device_setting.__anext__()

    page = await browser.new_page()
    await page.goto("http://auto.saveyourinsurance.com")
    # await page.goto("http://ifconfig.me/")

    # await page.wait_for_selector('#year')
    print("Page 1")

    wait = random.randint(2000, 10000)

    percent = int(open("percantage.txt", "r").read())
    false_array = [False] * (100-percent)
    true_array = [True] * percent
    tm = random.choice(false_array + true_array)
    if tm:
      page2 = await browser.new_page()
      await page2.goto('http://auto.saveyourinsurance.com/terms.html')
      ps = await page2.query_selector_all('p')
      for p in ps:
        if wait < 1:
          break
        await p.scroll_into_view_if_needed()
        rem = random.randint(2000, 3000)
        await page.wait_for_timeout(rem)
        wait -= rem
      await page2.close()

    await scroller(page, wait)

    year = random.randint(2012, int(datetime.datetime.today().year))
    yr = await page.query_selector('#year')
    await yr.scroll_into_view_if_needed()
    await page.select_option('#year', str(year))
    await page.evaluate('loadVehiclMakes()')
    await page.wait_for_timeout(random.randint(2000, 4000))

    
    make = await random_selector(page, '#make')
    await page.evaluate('loadModels()')
    await page.wait_for_timeout(random.randint(2000, 4000))

    model = await random_selector(page, '#model')
    await page.wait_for_timeout(random.randint(2000, 4000))

    insuredform = await random_selector(page, '#insuredform')

    await page.check('#leadid_tcpa_disclosure')
    submit_button = await page.click('#submit')

    #PAGE 2
    print("PAGE 2")
    await page.wait_for_timeout(random.randint(4000, 6000))

    await page.type('#firstname', first_name, delay=random.randint(20, 120))
    await page.wait_for_timeout(random.randint(2000, 4000))

    await page.type('#lastname', last_name, delay=random.randint(20, 120))
    await page.wait_for_timeout(random.randint(2000, 4000))
    
    month = random.randint(1,12)
    month = month if len(str(month)) > 1 else f"0{month}"

    day = random.randint(1,28)
    day = day if len(str(day)) > 1 else f"0{day}"

    year = int(datetime.datetime.today().year) - random.randint(23, 61)
    dob = "/".join(map(str, [month,day,year]))
    await page.type('#dateofbirth', dob, delay=random.randint(90, 200))
    await page.wait_for_timeout(random.randint(2000, 4000))


    try:
      gender = genderize(first_name)
    except NameError:
      gender = "Male"
    await page.select_option('#gender', gender)
    await page.wait_for_timeout(random.randint(2000, 4000))

    await page.type('#streetaddress', street_address, delay=random.randint(70, 200))
    await page.wait_for_timeout(random.randint(2000, 4000))

    await page.type('#zip', zipp, delay=random.randint(20, 120))
    await page.wait_for_timeout(random.randint(2000, 4000))

    await page.type('#phone', phone, delay=random.randint(20, 120))
    await page.wait_for_timeout(random.randint(2000, 4000))

    await page.type('#email', email, delay=random.randint(20, 120))

    await page.check('#liketoreceive')


    await page.wait_for_timeout(random.randint(2000, 5000))

    #Part 2
    print("Part 2")
    edu = await page.query_selector('#education')
    await edu.scroll_into_view_if_needed()

    education = await random_selector(page, '#education')
    await page.wait_for_timeout(random.randint(2000, 4000))

    rating = random.choice(['Good', 'Excellent'])
    await page.select_option('#creditrating', rating)
    await page.wait_for_timeout(random.randint(2000, 4000))

    await page.select_option('#married', "No")
    await page.wait_for_timeout(random.randint(2000, 4000))

    # await page.select_option('#tickets', "No")
    # await page.wait_for_timeout(random.randint(1000, 2000))

    submit_button = await page.query_selector('#submit >> nth=1')
    await submit_button.scroll_into_view_if_needed()
    await page.wait_for_timeout(random.randint(2000, 5000))
    data = []
    page.on('request', lambda req: data.append([req.post_data, req.post_data_json]) if req.url.endswith('submitDetails.php') else None)
    try:
      await submit_button.click(timeout=2000)
    except:
      while data == []:
        await page.wait_for_timeout(100)

    #PAGE 3
      await page.goto(f"http://auto.saveyourinsurance.com/submitDetails.php?{data[0][0]}", referer='http://auto.saveyourinsurance.com')
    await page.wait_for_timeout(random.randint(10000, 15000))

    print("Done")

    return year, make, model, insuredform, dob, gender, education, rating, random_device, data[0][1]["ipuser"]


if __name__ == "__main__":
  # print(playwright_devices()[1]["Blackberry PlayBook"])
  asyncio.run(main(first_name="testGreen", last_name="testG", street_address="test", city="test", zipp="85306", phone="8545214523", email="ds45s@gmail.com"))
  # print(playwright_devices())
  # print(genderize('John'))
