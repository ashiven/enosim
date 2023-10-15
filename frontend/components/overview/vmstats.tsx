import VMCard from "@components/overview/vmcard"

async function getData(vmName: string) {
   const res = await fetch(`http://127.0.0.1:5000/vminfo?name=${vmName}`)
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
   return (
      <div className="container mx-auto mt-12 mb-8">
         <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <VMCard data={filterVmJson(await getData("engine"))} />
            <VMCard data={filterVmJson(await getData("checker"))} />
            <VMCard data={filterVmJson(await getData("vulnbox1"))} />
            <VMCard data={filterVmJson(await getData("vulnbox2"))} />
         </div>
      </div>
   )
}
