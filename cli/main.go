package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/spf13/cobra"
)

var (
	apiURL     string
	contribute bool
	snapshotID string
	failOn     string
	maxCC      int
)

func main() {
	root := &cobra.Command{
		Use:   "cascudo",
		Short: "Cascudo — peixe que varre o fundo do código (0 IA)",
	}

	pushCmd := &cobra.Command{
		Use:   "push [path|zip]",
		Short: "Faz push de pasta/zip para API e mostra fluxograma",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error { return doPush(args[0]) },
	}
	pushCmd.Flags().StringVar(&apiURL, "api", "http://localhost:8000", "API base URL")
	pushCmd.Flags().BoolVar(&contribute, "contribute", false, "opt-in padrões anonimizados")

	ciCmd := &cobra.Command{
		Use:   "ci --snapshot <id> --fail-on dead,cycle,critical --max-cc 15",
		Short: "Gate em CI — bloqueia PR sujo (exit 1 se falhar)",
		RunE: func(cmd *cobra.Command, args []string) error { return doCI() },
	}
	ciCmd.Flags().StringVar(&snapshotID, "snapshot", "", "snapshot_id do push")
	ciCmd.Flags().StringVar(&failOn, "fail-on", "cycle,dead", "lista: cycle,dead,critical")
	ciCmd.Flags().IntVar(&maxCC, "max-cc", 15, "CC máximo")
	ciCmd.Flags().StringVar(&apiURL, "api", "http://localhost:8000", "API base URL")
	ciCmd.MarkFlagRequired("snapshot")

	patternsCmd := &cobra.Command{
		Use:   "patterns --snapshot <id>",
		Short: "Lista padrões do snapshot vs corpus",
		RunE: func(cmd *cobra.Command, args []string) error { return doPatterns() },
	}
	patternsCmd.Flags().StringVar(&snapshotID, "snapshot", "", "snapshot_id")
	patternsCmd.Flags().StringVar(&apiURL, "api", "http://localhost:8000", "API base URL")

	root.AddCommand(pushCmd, ciCmd, patternsCmd)

	if err := root.Execute(); err != nil {
		os.Exit(1)
	}
}

func doPush(target string) error {
	fi, err := os.Stat(target)
	if err != nil {
		return err
	}
	if fi.IsDir() {
		return fmt.Errorf("passe um .zip por enquanto: zip -r /tmp/out.zip %s && cascudo push /tmp/out.zip", target)
	}
	file, err := os.Open(target)
	if err != nil {
		return err
	}
	defer file.Close()
	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)
	part, err := writer.CreateFormFile("file", filepath.Base(target))
	if err != nil {
		return err
	}
	if _, err := io.Copy(part, file); err != nil {
		return err
	}
	writer.Close()
	url := fmt.Sprintf("%s/api/push?contribute=%t&ephemeral=true", apiURL, contribute)
	req, _ := http.NewRequest("POST", url, body)
	req.Header.Set("Content-Type", writer.FormDataContentType())
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	b, _ := io.ReadAll(resp.Body)
	fmt.Printf("→ %s %d\n%s\n", url, resp.StatusCode, string(b))
	if resp.StatusCode >= 400 {
		return fmt.Errorf("push falhou")
	}
	return nil
}

func doCI() error {
	payload := map[string]interface{}{
		"snapshot_id": snapshotID,
		"fail_on":     strings.Split(failOn, ","),
		"max_cc":      maxCC,
	}
	b, _ := json.Marshal(payload)
	resp, err := http.Post(apiURL+"/api/ci", "application/json", bytes.NewReader(b))
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	body, _ := io.ReadAll(resp.Body)
	fmt.Printf("→ %s/api/ci %d\n%s\n", apiURL, resp.StatusCode, string(body))
	var out map[string]interface{}
	json.Unmarshal(body, &out)
	if passed, ok := out["passed"].(bool); ok && !passed {
		fmt.Println("CI FAILED — PR bloqueado")
		os.Exit(1)
	}
	fmt.Println("CI PASSED")
	return nil
}

func doPatterns() error {
	if snapshotID == "" {
		return fmt.Errorf("--snapshot obrigatório")
	}
	resp, err := http.Get(fmt.Sprintf("%s/api/snapshots/%s/patterns", apiURL, snapshotID))
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	b, _ := io.ReadAll(resp.Body)
	fmt.Println(string(b))
	return nil
}
