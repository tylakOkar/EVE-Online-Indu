import sqlite3
import math

listfinalIngrediantsGroupNames = ["Moon Materials", "Mineral", "Basic Commodities - Tier 1", "Refined Commodities - Tier 2", "Tool"]
listfinalIngrediants = []

listIntermediateReactionsGroupNames= ["Intermediate Materials"]
listIntermediateReactions = []

listCompositeReactionGroupNames = ["Composite"]
listCompositeReactions = []

listFuelBlocksGroupNames = ["Fuel Block"]
listFuelBlocks = []

listComponentsGroupNames = ["Construction Components", "Battleship"]
listComponents = []

class Ingrediant:
    def __init__(self, materialName, quant):
        self.materialName = materialName
        self.quant = quant

def addMaterialToList(ingrediantList, material, quant):
    # Adds a Material and its quant to the final ingrediant list
    found = False
    for ingrediant in ingrediantList:
        if ingrediant.materialName == material:
            found = True
            ingrediant.quant = ingrediant.quant + quant
            break
    if not found:
        ingrediantList.append(Ingrediant(material, quant))
    return ingrediantList

def getBlueprintRuns(product, quant): 
    cur.execute("""
            SELECT
                iap.typeID,
                product.typeName,
                product.typeID,
                iap.quantity 
            FROM industryActivityProducts iap 
                LEFT OUTER JOIN invTypes product ON iap.productTypeID = product.typeID
                LEFT OUTER JOIN invTypes blueprint ON iap.typeID = blueprint.typeID
            WHERE product.typeName LIKE '""" + product + """' AND blueprint.published = 1
        """)
    blueprint = cur.fetchall()
    if  blueprint:
        productsPerRun = blueprint[0][3]
        runs = math.ceil(quant/productsPerRun)
        return runs
    return

def getMaterialList(product):
    cur.execute("""
        SELECT
            iap.typeID,
            product.typeName,
            product.typeID,
            blueprint.typeName,
            iam.materialTypeID,
            material.typeName,
            iam.quantity,
            ig.groupName 
        FROM industryActivityProducts iap 
            LEFT OUTER JOIN invTypes product ON iap.productTypeID = product.typeID
            LEFT OUTER JOIN invTypes blueprint ON iap.typeID = blueprint.typeID
            LEFT OUTER JOIN industryActivityMaterials iam ON iam.typeID = blueprint.typeID 
            LEFT OUTER JOIN invTypes material ON iam.materialTypeID = material.typeID
            LEFT OUTER JOIN invGroups ig ON material.groupID = ig.groupID
        WHERE product.typeName LIKE '""" + product + """' AND (iam.activityID = 1 or iam.activityID = 11) AND blueprint.published = 1 AND product.published = 1 AND material.published = 1 AND ig.published = 1
    """)
    queryResult = cur.fetchall()
    return queryResult

def putMaterialsInCorrectList(structureBonus, materialEfficieny, materialList, product, quant, listfinalIngrediantsGroupNames, listfinalIngrediants, listComponentsGroupNames, listComponents, listFuelBlocksGroupNames, listFuelBlocks, listCompositeReactionGroupNames, listCompositeReactions, listIntermediateReactionsGroupNames, listIntermediateReactions):
    for i in materialList:
        groupName = i[7]
        materialName = i[5]
        blueprintRuns = getBlueprintRuns(product, quant)
        materialQuant = i[6] * blueprintRuns

        if i[6] != 1:
            materialQuant = materialQuant / 100 * (100 - materialEfficieny)
            materialQuant = materialQuant / 100 * (100 - structureBonus)
            materialQuant = math.ceil(materialQuant)
        
        if groupName in listfinalIngrediantsGroupNames:
            listfinalIngrediants = addMaterialToList(listfinalIngrediants, materialName, materialQuant)
            continue

        if groupName in listComponentsGroupNames:
            listComponents = addMaterialToList(listComponents, materialName, materialQuant)
            continue

        if groupName in listFuelBlocksGroupNames:
            listFuelBlocks = addMaterialToList(listFuelBlocks, materialName, materialQuant)
            continue

        if groupName in listCompositeReactionGroupNames:
            listCompositeReactions = addMaterialToList(listCompositeReactions, materialName, materialQuant)
            continue

        if groupName in listIntermediateReactionsGroupNames:
            listIntermediateReactions = addMaterialToList(listIntermediateReactions, materialName, materialQuant)
            continue


con = sqlite3.connect("D:\EVE Projekt\sqlite-latest.sqlite")

cur = con.cursor()
finalProduct = "Paladin"
finalProductQuant = 2
finalProductMaterialEfficiency = 4

componentsStructureBonus = 1
reactionStructureBonus = 2.6
componentsMaterialEfficiency = 10
reactionsMaterialEfficieny = 0


neededMaterials = getMaterialList(finalProduct)
putMaterialsInCorrectList(componentsStructureBonus, finalProductMaterialEfficiency, neededMaterials, finalProduct, finalProductQuant, listfinalIngrediantsGroupNames, listfinalIngrediants, listComponentsGroupNames, listComponents, listFuelBlocksGroupNames, listFuelBlocks, listCompositeReactionGroupNames, listCompositeReactions, listIntermediateReactionsGroupNames, listIntermediateReactions)

while (listComponents):
    copyListComponents = listComponents.copy()
    for i in copyListComponents:
        listComponents.remove(i)
        materialList = getMaterialList(i.materialName)
        putMaterialsInCorrectList(componentsStructureBonus, componentsMaterialEfficiency, materialList, i.materialName, i.quant, listfinalIngrediantsGroupNames, listfinalIngrediants, listComponentsGroupNames, listComponents, listFuelBlocksGroupNames, listFuelBlocks, listCompositeReactionGroupNames, listCompositeReactions, listIntermediateReactionsGroupNames, listIntermediateReactions)

while (listCompositeReactions):
    copyListCompositeReactions = listCompositeReactions.copy()
    for i in copyListCompositeReactions:
        listCompositeReactions.remove(i)
        materialList = getMaterialList(i.materialName)
        putMaterialsInCorrectList(reactionStructureBonus ,reactionsMaterialEfficieny, materialList, i.materialName, i.quant, listfinalIngrediantsGroupNames, listfinalIngrediants, listComponentsGroupNames, listComponents, listFuelBlocksGroupNames, listFuelBlocks, listCompositeReactionGroupNames, listCompositeReactions, listIntermediateReactionsGroupNames, listIntermediateReactions)

while (listIntermediateReactions):
    copyListIntermediateReactions = listIntermediateReactions.copy()
    for i in copyListIntermediateReactions:
        listIntermediateReactions.remove(i)
        materialList = getMaterialList(i.materialName)
        putMaterialsInCorrectList(reactionStructureBonus ,reactionsMaterialEfficieny, materialList, i.materialName, i.quant, listfinalIngrediantsGroupNames, listfinalIngrediants, listComponentsGroupNames, listComponents, listFuelBlocksGroupNames, listFuelBlocks, listCompositeReactionGroupNames, listCompositeReactions, listIntermediateReactionsGroupNames, listIntermediateReactions)

for i in listfinalIngrediants:
    print(i.materialName + " " + str(i.quant))
for i in listFuelBlocks:
    print(i.materialName + " " + str(i.quant))


# I hate dis