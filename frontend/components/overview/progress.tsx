import SimulationProgressClient from "@/components/overview/progressclient"

async function getData() {
   try {
      const res = await fetch("http://127.0.0.1:5000/roundinfo", {
         next: { revalidate: 0 },
      })
      return res.json()
   } catch (e) {
      return {}
   }
}

export default async function SimulationProgress() {
   const data = await getData()
   return (
      Object.keys(data).length > 0 && <SimulationProgressClient data={data} />
   )
}
