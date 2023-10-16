import VMCard from "@components/overview/vmcard"

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
   return dataList[0]
}

function filterVmJson(data: any) {
   const filteredData = {
      name: data.name,
      status: data.status,
      cpu: data.cpu,
      ram: data.ram,
      disk: data.disk,
      uptime: data.uptime,
      ip: data.ip,
   }
   return filteredData
}

export default async function VMStats() {
   const vmList = await getVmList()

   return (
      <div className="container mx-auto mt-12 mb-8">
         <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {vmList.map(async (vmName: string) => (
               <VMCard data={filterVmJson(await getData(vmName))} />
            ))}
         </div>
      </div>
   )
}
