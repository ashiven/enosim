import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"

export default function SimulationProgress() {
   return (
      <div className="mt-8">
         <div className="flex h-5 items-center space-x-4 text-sm mb-4">
            <div>Round 10</div>
            <Separator orientation="vertical" />
            <div>20 Rounds remaining</div>
            <Separator orientation="vertical" />
            <div>40s Until next round</div>
         </div>
         <Progress value={50} />
      </div>
   )
}
