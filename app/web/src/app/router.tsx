import { createBrowserRouter } from "react-router-dom";
import { Shell } from "@/widgets/Shell";
import { UploadPage } from "@/pages/UploadPage";
import { FlowPage } from "@/pages/FlowPage";
import { PatternsPage } from "@/pages/PatternsPage";
import { DeadPage } from "@/pages/DeadPage";
import { GraphPage } from "@/pages/GraphPage";
import { DiffPage } from "@/pages/DiffPage";

export const router = createBrowserRouter([
  {
    element: <Shell />,
    children: [
      { path: "/", element: <UploadPage /> },
      { path: "/upload", element: <UploadPage /> },
      { path: "/flow", element: <FlowPage /> },
      { path: "/graph", element: <GraphPage /> },
      { path: "/dead", element: <DeadPage /> },
      { path: "/patterns", element: <PatternsPage /> },
      { path: "/diff", element: <DiffPage /> },
    ],
  },
]);
