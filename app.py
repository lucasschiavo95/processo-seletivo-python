from flask import Flask, jsonify, Response
import requests
import csv
import io

app = Flask(__name__)

def get_api_data(endpoint):
    try:
        base_url = "https://sidebar.stract.to/api"
        token = "ProcessoSeletivoStract2025"
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Fazendo requisição para: {base_url}{endpoint}")
        print(f"Headers: {headers}")
        response = requests.get(f"{base_url}{endpoint}", headers=headers)
        response.raise_for_status()
        print(f"Resposta da API: {response.json()}")
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error: {http_err.response.text}")
        return {"error": f"HTTP error occurred: {http_err}"}
    except Exception as err:
        print(f"Error: {err}")
        return {"error": f"Other error occurred: {err}"}


@app.route('/')
def root():
    return jsonify({
        "name": "Seu Nome",
        "email": "seu.email@example.com",
        "linkedin": "https://www.linkedin.com/in/lucas-schiavo/"
    })


@app.route('/api')
def api_root():
    return jsonify({
        "message": "Bem-vindo à API de Relatórios",
        "endpoints": [
            "/api/platforms",
            "/api/accounts?platform={platform}",
            "/api/fields?platform={platform}",
            "/api/insights?platform={platform}&account={account}&token={token}&fields={field1,field2,etc}"
        ]
    })


@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    print("Buscando plataformas...")
    platforms = get_api_data('/platforms')
    if "error" in platforms:
        return jsonify({"error": platforms["error"]}), 500
    return jsonify(platforms)


@app.route('/platform', methods=['GET'])
def get_platform_list():
    platforms_data = get_api_data('/platforms')
    if "error" in platforms_data:
        return jsonify({"error": platforms_data["error"]}), 500

    valid_platforms = [p["value"] for p in platforms_data.get("platforms", [])]

    return jsonify({"available_platforms": valid_platforms})


@app.route('/<platform>')
def platform_table(platform):
    if platform == "api":
        return jsonify({"error": "Invalid request"}), 404

    platforms_data = get_api_data('/platforms')
    if "error" in platforms_data:
        return jsonify({"error": platforms_data["error"]}), 500

    valid_platforms = [p["value"] for p in platforms_data.get("platforms", [])]

    if platform not in valid_platforms:
        return jsonify({
            "error": "invalid platform",
            "available_platforms": valid_platforms,
            "requested_platform": platform
        }), 400


@app.route('/<platform>/resumo', methods=['GET'])
def platform_summary(platform):
    platforms = get_api_data('/platforms')
    if "error" in platforms:
        return jsonify({"error": platforms["error"]}), 500

    valid_platforms = [p["value"] for p in platforms.get("platforms", [])]

    if platform not in valid_platforms:
        return jsonify({
            "error": "invalid platform",
            "available_platforms": valid_platforms,
            "requested_platform": platform
        }), 400

    print(f"Requesting summary data for platform: {platform}")

    accounts_data = get_api_data(f"/accounts?platform={platform}")
    print(f"Accounts data received: {accounts_data}")

    if "error" in accounts_data:
        return jsonify({"error": f"Error retrieving accounts for {platform}: {accounts_data['error']}"}), 500

    if isinstance(accounts_data, dict):
        print(f"Resposta da API é um dicionário: {accounts_data}")

        accounts = accounts_data.get('accounts', [])
        if not accounts:
            return jsonify({"error": "Não foi possível encontrar contas na resposta"}), 500
    else:
        print(f"Resposta da API não é um dicionário nem uma lista, é do tipo {type(accounts_data)}")
        return jsonify({"error": "Erro na estrutura da resposta de contas"}), 500

    fields = get_api_data(f"/fields?platform={platform}")
    if "error" in fields:
        return jsonify({"error": f"Error retrieving fields for {platform}: {fields['error']}"}), 500

    summary = []
    platform_totals = {field: 0 for field in fields}

    for account in accounts:
        if isinstance(account, dict):
            if 'id' in account:
                insights = get_api_data(
                    f"/insights?platform={platform}&account={account['id']}&fields={','.join(fields)}")
                if "error" in insights:
                    return jsonify(
                        {"error": f"Error retrieving insights for account {account['id']}: {insights['error']}"}), 500

                account_totals = {field: 0 for field in fields}
                for insight in insights:
                    for field in fields:
                        if isinstance(insight.get(field), (int, float)):
                            account_totals[field] += insight.get(field, 0)

                summary_row = [platform, account['name']] + [account_totals[field] for field in fields]
                summary.append(summary_row)
            else:
                print(f"A conta {account} não possui 'id'.")
        else:
            print(f"A conta {account} não é um dicionário.")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Platform', 'Account Name'] + fields)
    writer.writerows(summary)
    output.seek(0)

    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=summary.csv"})


@app.route('/geral')
def general_report():
    platforms = get_api_data('/platforms')
    if "error" in platforms:
        return jsonify({"error": platforms["error"]}), 500

    all_ads = []
    all_fields = set()

    for platform in platforms:
        fields = get_api_data(f"/fields?platform={platform}")
        if "error" not in fields:
            all_fields.update(fields)

    all_fields = list(all_fields)

    for platform in platforms:
        accounts = get_api_data(f"/accounts?platform={platform}")
        if "error" in accounts:
            continue

        fields = get_api_data(f"/fields?platform={platform}")
        if "error" in fields:
            continue

        for account in accounts:
            insights = get_api_data(
                f"/insights?platform={platform}&account={account['id']}&fields={','.join(fields)}")
            if "error" in insights:
                continue
            for insight in insights:
                row_data = {field: '' for field in all_fields}
                row_data.update(insight)
                row = [platform, account['name']] + [row_data.get(field, '') for field in all_fields]
                all_ads.append(row)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Platform', 'Account Name'] + all_fields)
    writer.writerows(all_ads)
    output.seek(0)

    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=general_report.csv"})


@app.route('/geral/resumo')
def general_summary():
    platforms = get_api_data('/platforms')
    if "error" in platforms:
        return jsonify({"error": platforms["error"]}), 500

    all_fields = set()

    for platform in platforms:
        fields = get_api_data(f"/fields?platform={platform}")
        if "error" not in fields:
            all_fields.update(fields)

    all_fields = list(all_fields)

    platform_summaries = []
    for platform in platforms:
        accounts = get_api_data(f"/accounts?platform={platform}")
        if "error" in accounts:
            continue

        platform_totals = {field: 0 for field in all_fields}

        for account in accounts:
            fields = get_api_data(f"/fields?platform={platform}")
            if "error" in fields:
                continue

            insights = get_api_data(
                f"/insights?platform={platform}&account={account['id']}&fields={','.join(fields)}")
            if "error" in insights:
                continue

            for insight in insights:
                for field in all_fields:
                    if isinstance(insight.get(field), (int, float)):
                        platform_totals[field] += insight.get(field, 0)

        summary_row = [platform, ''] + [platform_totals.get(field, '') for field in all_fields]
        platform_summaries.append(summary_row)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Platform', 'Account Name'] + all_fields)
    writer.writerows(platform_summaries)
    output.seek(0)

    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=general_summary.csv"})


if __name__ == "__main__":
    app.run(debug=True)
