import SimulationProgressClient from "@/components/overview/progressclient"

const URL = process.env.API_URL || "http://127.0.0.1:5000"

async function getData() {
   try {
      const res = await fetch(`${URL}/roundinfo`, {
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
