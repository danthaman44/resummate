import { GitIcon } from "@/components/icons";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { memo } from "react";

function PureSourceCodeButton() {
  return (
    <div className="fixed bottom-4 left-4 z-50">  
      <Link href="https://github.com/danthaman44/resummate/">
        <Button variant="outline">
          <GitIcon /> View Source Code
        </Button>
      </Link>
    </div>
  )
}

export const ViewSourceCodeButton = memo(PureSourceCodeButton)