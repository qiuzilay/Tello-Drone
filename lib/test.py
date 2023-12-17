from toolbox import console, Enum, array, json
from movements import Movements, Context




context = ['往前', '飛行', '30', '公尺', '然後', '順時針', '旋轉', '90', '度']

console.debug(context)

result = Context(context).filter().standardize()

console.debug(result.context.standardize)


