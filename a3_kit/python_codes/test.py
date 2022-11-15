
import requests
import xlsxwriter
BOT_ID = 'x1563185332983'
journeys_api = 'https://app.yellowmessenger.com/api/ai/journey/all?bot='+BOT_ID
training_api = 'https://app.yellowmessenger.com/api/ai/training/get/'
prediction_api = 'https://app.yellowmessenger.com/api/ml/prediction?bot='+BOT_ID+'&text='
headers = {'Content-Type': 'application/json', 'x-auth-token': '7242aa64b3604a5c87dc90da689f05ef1b45c5751839ef53144a00feb2a21833'}
ques=["Can I carry (Item names)?","Is (Item names) allowed?","Can we carry (Item names)?" ,"Am I allowed to carry (Item names)?",
      "Am I allowed (Item names)?","Will you allow (Item names)?", "I want to carry (Item names)?", "We want to carry (Item names)?",
      "I wish to carry (Item names)?", "We wish to carry (Item names)?","Do you allow (Item names)?"]
items="Realistic Replicas of Explosives, Wheelchair, Silver Jewelry, ganga jal, Brass Knuckles, Gas stove, Starter pistols, Safety Razors (including disposable razors), Compressed Air Guns, Swords, Perfume, Laptop more than 2, Drone camera, Umbrellas, Meat Cleavers, Trimmer with battery, Plastic Explosives, Meat, Grinder, Stun Guns, Photo frames, Monitor, Walking Canes, Sword, Musical Instruments, Pulses, Water bottle, Dynamite, Braille Note, Augmentation Deices, Slate and Stylus, Fireworks, Diabetes, Compressed Gas Cylinders, Lighters, Night Sticks, Fruits, Deo, Broadband routers, Strike-anywhere Matches, spray for medical use, Nitroglycerine pills, Golf Kit, idols, Coconut, Blade, Raw Foods, Pagers, Ski Poles, Aerosol, Groceries, Kubatons, Eyeglass Repair Tools, Ice Axes, Pram, Mobile charger, Baby Stroller, Sharp items, Laptop, Computers, Rod items, Personal care, toiletries, Plants, Jewellery, Spray Paint, Medicines, Medical Equipment, Eyelash Curlers, Skeleton, Ghee, Cigar Cutters, BB guns, Telephone, Chlorine, Prosthetic Device Tools, Turpentine, Paint Thinner, Hockey Sticks, Lacrosse Sticks, Box Cutters, Toy Transformer Robots, Golf Clubs, Crowbars, Pets, Fuels, flammable liquid fuel, Cooking fuels , Mobile Phones, Chopper Knife, Cigarettes, Toy Weapons, Sweets, Home appliances, Lighter Fluid, Shocking Devices, Vegetables, Rice, Non-prescribed medicines, Firearms, Steel heavy items, Power bank, Trimmer without battery, Statues, Ashes, Cattle Prods, Pepper Spray, Mace, Wrist watches, Flare Guns, Multiple tabs, Multiple mobiles, Hair dryer, TV, Pickles, Pellet Guns, Nunchakus, Aerated drinks, Dry foods, DSLR, Throwing Stars, Painting brush, Tear Gas, Oily items, Martial Arts Weapons, Blasting Caps, Metal items, Hammers, Heater electric, Spillable Batteries, Gun Powder, Gas Torches, Desktop, Cuticle Cutters, Car Seat, Realistic Replicas of Incendiaries, Heater battery, Bicycle, Gold, Bows, Arrows, Dry fruits, Camera Equipment, E-cigarettes, Personal Data Assistants , Tweezers, Holy water, Gun Lighters, Driller machines, Screwdrivers, Glass items, Cricket Bats, Spear Guns, Mechanical Tools, Liquor, Sabers, Drills, Saws, Laptop charger, Realistic Replicas of Firearms, Cake, Raw Green vegetables, Guns, Parts of Guns and Firearms, CPU, Flares, Corkscrews, Human Remains, Honey, Camcorders, Hand Grenades, Kirpan, Nail Files, Gasoline, Axes, hatchets, Tools, Wrenches, Pliers, Cash, Knives, Fish, Silver ware crockery, Liquid Bleach, Billy Clubs, UPS, Baseball Bats, Pool Cues, Razor, Knitting Needles, Crochet Needles, Needles, Blades, box cutters, Utility knives, Razor blades, Black Jacks, Shaving brush, Ice Picks, Nail Clippers, Plastic cutlery, Roundbladed, Power drills, Power saws"
items_arr=items.split(",")
workbook = xlsxwriter.Workbook('TestReport.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write('A1', 'Keyword')
worksheet.write('B1', 'Status')
worksheet.write('C1', 'Journey')
count=1
for i in ques:
    for j in items_arr:
        item_name=j.strip()
        line=i.replace("(Item names)",item_name)
        count=count+1
        entity=""
        try:
            pred_url = prediction_api+line+"&language=en"
            pred_res = requests.get(pred_url, headers = headers)
            pred_res = pred_res.json()
            entity=pred_res['entities']
            intent = pred_res['intent']
            confidence = pred_res['confidence']

            if(entity['restricted_items'] and (confidence<0.65 or (confidence>=0.65 and intent=="know-the-items-that-can-be-carried"))):
                worksheet.write('A'+str(count), line)
                worksheet.write('B'+str(count), 'Pass')
                worksheet.write('C'+str(count), 'know-the-items-that-can-be-carried')
            else:
                worksheet.write('A'+str(count), line)
                worksheet.write('B'+str(count), '')
                worksheet.write('C'+str(count), "Other Journey Triggered")

        except:
            if(confidence<0.65):
                worksheet.write('A' + str(count), line)
                worksheet.write('B' + str(count), 'Fail')
                worksheet.write('C' + str(count), "Unidentified Keyword (Uh Oh! I donâ€™t quite ....)")
            elif (confidence>=0.65 and intent=="know-the-items-that-can-be-carried"):
                worksheet.write('A' + str(count), line)
                worksheet.write('B' + str(count), 'Pass')
                worksheet.write('C' + str(count), 'know-the-items-that-can-be-carried')
            else:
                worksheet.write('A' + str(count), line)
                worksheet.write('B' + str(count), 'Fail')
                worksheet.write('C' + str(count), "Other Journey Triggered")

workbook.close()
print("++++++++++Done Execution Successfully++++++++++++")


