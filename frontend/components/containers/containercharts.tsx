import ContainerSelect from "@/components/containers/containerselect"

const URL = process.env.API_URL || "http://127.0.0.1:5000"

async function getContainerList() {
   try {
      const res = await fetch(`${URL}/containerlist`, {
         next: { revalidate: 0 },
      })
      const containerList = eval(await res.text())
      return containerList
   } catch (e) {
      return []
   }
}

async function getData(containerName: string) {
   try {
      const res = await fetch(`${URL}/containerinfo?name=${containerName}`, {
         next: { revalidate: 0 },
      })
      const dataList = eval(await res.text())
      return dataList
   } catch (e) {
      return []
   }
}

function filterData(data: any) {
   const cpuData = data.map((item: any) => ({
      date: item.measuretime,
      percentage: item.cpuusage,
   }))
   const ramData = data.map((item: any) => ({
      date: item.measuretime,
      percentage: item.ramusage,
   }))
   const netData = data.map((item: any) => ({
      date: item.measuretime,
      rx: item.netrx,
      tx: item.nettx,
   }))

   return { cpuData, ramData, netData }
}

export default async function ContainerCharts() {
   const containerList = await getContainerList()
   const containerData: any = {}

   await Promise.all(
      containerList.map(async (containerName: string) => {
         containerData[containerName] = filterData(await getData(containerName))
      })
   )

   return (
      <ContainerSelect
         containerList={containerList}
         containerData={containerData}
      />
   )
}
