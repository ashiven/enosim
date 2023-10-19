import VMChart from "@/components/overview/vmchart"

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
      value: item.cpuusage,
   }))
   const ramData = data.map((item: any) => ({
      date: item.measuretime,
      value: item.ramusage,
   }))
   const netData = data.map((item: any) => ({
      date: item.measuretime,
      line1: item.netrx,
      line2: item.nettx,
   }))

   return { cpuData, ramData, netData }
}

export default async function VMCharts() {
   const vmList = await getVmList()

   return (
      <div>
         {vmList.map(async (vmName: string) => (
            <div>
               <span className="text-xl font-bold">{vmName}-stats:</span>
               <VMChart data={filterData(await getData(vmName))} />
            </div>
         ))}
      </div>
   )
}
