import VMChart from "@/components/overview/vmchart"

async function getVmList() {
   const res = await fetch(`http://127.0.0.1:5000/vmlist`)
   if (!res.ok) {
      throw new Error("Failed to fetch data")
   }
   const vmList = eval(await res.text())
   return vmList
}

async function getData(vmName: string) {
   const res = await fetch(`http://127.0.0.1:5000/vminfo?name=${vmName}`, {
      next: { revalidate: 0 },
   })
   if (!res.ok) {
      throw new Error("Failed to fetch data")
   }
   const dataList = eval(await res.text())
   return dataList
}

function filterData(data: any) {
   const cpuData = data.map((item: any) => ({
      date: item.measuretime,
      value: item.cpuusage,
   }))
   const ramData = data.map((item: any) => ({
      date: item.measuretime,
      value: item.ramusage,
   }))
   const netData = data.map((item: any) => ({
      date: item.measuretime,
      value: item.netrx,
   }))

   return { cpuData, ramData, netData }
}

export default async function VMCharts() {
   const vmList = await getVmList()

   return (
      <div>
         {vmList.map(async (vmName: string) => (
            <VMChart data={filterData(await getData(vmName))} />
         ))}
      </div>
   )
}
