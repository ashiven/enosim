import VMSelect from "@/components/overview/vmchartselect"

async function getVmList() {
   try {
      const res = await fetch(`http://127.0.0.1:5000/vmlist`, {
         next: { revalidate: 0 },
      })
      const vmList = eval(await res.text())
      return vmList
   } catch (e) {
      return []
   }
}

async function getData(vmName: string) {
   try {
      const res = await fetch(`http://127.0.0.1:5000/vminfo?name=${vmName}`, {
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

export default async function VMCharts() {
   const vmList = await getVmList()
   const vmDataPromises = vmList.map(async (vmName: string) => ({
      [vmName]: filterData(await getData(vmName)),
   }))
   const vmDataArray = await Promise.all(vmDataPromises)
   const vmData = vmDataArray.reduce((acc, vmDataItem) => {
      return { ...acc, ...vmDataItem }
   }, {})

   return <VMSelect vmList={vmList} vmData={vmData} />
}
