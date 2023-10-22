import VMCard from "@components/overview/vmcard"

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
      return dataList[0]
   } catch (e) {
      return {}
   }
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
   const vmData: any = {}

   await Promise.all(
      vmList.map(async (vmName: string) => {
         vmData[vmName] = filterVmJson(await getData(vmName))
      })
   )

   return (
      <div className="container mx-auto mt-12 mb-8">
         <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {vmList.map((vmName: string) => (
               <VMCard data={vmData[vmName]} />
            ))}
         </div>
      </div>
   )
}
